(ns geomw-clj.test
  (:use geomw-clj.core
        [clojure.data.json :only [pprint]]))

(defn run []
  (time 
   (print
    (query-ways-complete false nil nil))))
