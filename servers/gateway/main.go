package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"

	_ "github.com/go-sql-driver/mysql"
)

// Director type for creating reverse proxies to put into handle functions in gateway for microservices.
type Director func(r *http.Request)

func main() {

	// Getting the port to listen in on. We have fake certs just for :443 on https.
	httpsAddr := os.Getenv("ADDR")
	if len(httpsAddr) == 0 {
		httpsAddr = ":4000"
	}

	flaskAddr := os.Getenv("FLASKADDR")
	if len(flaskAddr) == 0 {
		flaskAddr = "flask:80"
	}

	// mongoAddr := os.Getenv("MONGOADDR")
	// if len(mongoAddr) == 0 {
	// 	mongoAddr = "MONGO:27017"
	// }

	flaskServerAddr, _ := url.Parse("http://" + flaskAddr)
	flaskProxy := &httputil.ReverseProxy{Director: CustomDirector(flaskServerAddr)}
	mux := http.NewServeMux()

	mux.Handle("/v1/flask", flaskProxy)

	log.Printf(httpsAddr, flaskAddr)
	log.Printf("Tutupoopoo Server is listening on %s...", httpsAddr)
	log.Fatal(http.ListenAndServe(httpsAddr, mux))
}

// CustomDirector returns a function for use in httputil.ReverseProxy which requires a director.
// ***TO DO: Add in authentication logic from initial assignment.***
func CustomDirector(target *url.URL) Director {
	return func(r *http.Request) {
		r.Host = target.Host
		r.URL.Host = target.Host
		r.URL.Scheme = target.Scheme
	}
}
