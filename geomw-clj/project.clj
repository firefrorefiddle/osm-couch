(defproject geomw-clj "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.6.0"]
                 [ring "1.2.1"]
                 [ring/ring-json "0.2.0"]
                 [compojure "1.1.6"]
                 [hiccup "1.0.5"]
                 [enlive "1.1.5"]
                 [clj-http "2.0.0"]
                 [org.clojure/data.json "0.2.6"]
                 [tikkba "0.5.0" :exclusions [org.clojure/clojure]]]
  :plugins [[lein-swank "1.4.5"]
            [lein-ring "0.8.10"]]
  :ring {:handler geomw-clj.core/app
         :nrepl { :start? true }}
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}}
  :main geomw-clj.test/run)
