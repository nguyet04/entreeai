package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"time"

	"gopkg.in/mgo.v2"

	"github.com/go-redis/redis"
	_ "github.com/go-sql-driver/mysql"
)

// Director type for creating reverse proxies to put into handle functions in gateway for microservices.
type Director func(r *http.Request)

func main() {
	signingKey := os.Getenv("SESSIONKEY")
	if len(signingKey) == 0 {
		signingKey = "healthy"
	}

	redisAddr := os.Getenv("REDISADDR")
	if len(redisAddr) == 0 {
		redisAddr = "redissvr:6379"
	}
	redisClient := redis.NewClient(&redis.Options{
		Addr:     redisAddr,
		Password: "",
		DB:       0,
	})

	tlsKeyPath := os.Getenv("TLSKEY")
	tlsCertPath := os.Getenv("TLSCERT")
	if tlsKeyPath == "" || tlsCertPath == "" {
		log.Print("environment variables tlskey and tlscert have not yet been set")
		os.Exit(1)
	}

	// Getting the port to listen in on. We have fake certs just for :443 on https.
	httpsAddr := os.Getenv("ADDR")
	if len(httpsAddr) == 0 {
		httpsAddr = ":443"
	}

	dsn := os.Getenv("DSN")
	if len(dsn) == 0 {
		dsn = fmt.Sprintf("root:%s@tcp(mysqlstore:3306)/userstore", os.Getenv("MYSQL_ROOT_PASSWORD"))
	}

	tradeAddr := os.Getenv("TRADEADDR")
	if len(tradeAddr) == 0 {
		tradeAddr = "FLASK:80"
	}

	log.Printf(dsn)
	var currDB *users.MySQLStore
	mysqldb, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("%v", err)
	}
	for i := 1; i <= 20; i++ {
		connErr := mysqldb.Ping()
		if connErr == nil {
			log.Printf("Connection to SQL successful.")
			break
		}
		log.Printf("Error connecting to mysql server at %s: %s", dsn, connErr)
		log.Printf("Will attempt another connection in %d seconds", i*2)
		time.Sleep(time.Duration(i*2) * time.Second)
	}
	currDB = users.NewDBStore(mysqldb)

	mongoAddr := os.Getenv("MONGOADDR")
	mongoName := os.Getenv("MONGONAME")
	if len(mongoAddr) == 0 {
		httpsAddr = "mongochar:27017"
	}
	if len(mongoName) == 0 {
		mongoName = "mongo"
	}

	sess, err := mgo.Dial(mongoAddr)
	if err != nil {
		log.Fatalf("error dialing mongo: %v\n", err)
	} else {
		fmt.Printf("connected successfully to mongoserver!")
	}

	mqAddr := os.Getenv("MQADDR")
	if len(mqAddr) == 0 {
		mqAddr = "rabbitmq:5672"
	}
	msgQueueName := os.Getenv("QUEUENAME")
	if len(msgQueueName) == 0 {
		msgQueueName = "msgQueue"
	}

	currSocketStore := handlers.SocketStore{
		Connections: make(map[string]*handlers.WSClient),
	}

	mdb := characters.NewCharacterStore(sess, mongoName)
	rs := sessions.NewRedisStore(redisClient, time.Hour)
	// Create all connections to the various stores.
	hctx := handlers.NewHandlerContext(signingKey, rs, currDB, mdb, currSocketStore)
	hctx.ConsumeMessages(msgQueueName, mqAddr)

	tradeServerAddr, _ := url.Parse("http://" + flaskAddr)
	log.Printf("Trade server proxy is at: %+v", tradeServerAddr)
	tradeProxy := &httputil.ReverseProxy{Director: CustomDirector(tradeServerAddr, hctx)}

	mux := http.NewServeMux()

	mux.Handle("/v1/trade", tradeProxy)

	mux.HandleFunc("/v1/ws", hctx.WebSocketConnectionHandler)

	mux.HandleFunc("/v1/users", hctx.UsersHandler)

	wrapper := handlers.NewLogger(mux)

	log.Printf("server is listening on %s...", httpsAddr)
	log.Fatal(http.ListenAndServeTLS(httpsAddr, tlsCertPath, tlsKeyPath, wrapper))
}

// CustomDirector returns a function for use in httputil.ReverseProxy which requires a director.
// ***TO DO: Add in authentication logic from initial assignment.***
func CustomDirector(target *url.URL, hctx *handlers.HandlerContext) Director {
	return func(r *http.Request) {
		r.Header.Del("X-User")
		r.Header.Del("X-Character")
		r.Header.Add("X-Forwarded-Host", r.Host)
		r.Host = target.Host
		r.URL.Host = target.Host
		r.URL.Scheme = target.Scheme
		currSess := &handlers.SessionState{}
		_, err := sessions.GetState(r, hctx.Key, hctx.CurrentSessionStore, currSess)
		if err != nil {
			log.Print(err)
			return
		}

		marshalled, _ := json.Marshal(currSess.CurrentUser)
		char, err := hctx.CurrentMongoStore.FindCharacterByCID(currSess.CurrentCharacterID)
		marshalledchar, _ := json.Marshal(char)
		if err != nil {
			log.Print(err)
			return
		}
		r.Header.Set("X-User", string(marshalled))
		r.Header.Set("X-Character", string(marshalledchar))
	}
}