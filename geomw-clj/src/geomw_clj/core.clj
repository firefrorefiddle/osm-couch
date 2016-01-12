(ns geomw-clj.core
  (:use ring.adapter.jetty
        ring.middleware.resource
        [ring.middleware.content-type :only [wrap-content-type]]
        [ring.middleware.json :refer [wrap-json-response]]
        hiccup.core
        [hiccup.page :only [include-css include-js]]
        compojure.core
;        [analemma svg]
        [tikkba dom])
  (:require [compojure.route    :as route]
            [clj-http.client    :as client]
            [clojure.data.json  :as json]
            [ring.util.response :as resp]
            [analemma.charts    :as charts]
            [analemma.xml       :as xml]
            ))

(def ^:dynamic *level* 1)

(defn server-db [] (str "http://localhost:5984/saalfelden_" *level* "/"))

(defn query-coords [docid]
  (-> (str (server-db) docid)
      (client/get)
      (:body)
      (json/read-str)
      (get "coords")))

(defn query-ways [wid]
  (-> (client/get (str (server-db) "_design/osmcouch/_view/ways"
                       (when wid (str "?startkey=\"" wid "\"&endkey=\"" wid "\""))))
      (:body)
      (json/read-str)))

(defn complete-rows [rows]
  (map 
     (fn [row] (update-in row ["value" "nodes"] #(pmap query-coords %)))
   rows))

(defn query-ways-complete [by-name? startkey endkey]
  (let [source (if by-name? "ways_by_name" "ways")
        skstr (when startkey (str "startkey=\"" startkey "\""))
        ekstr (when endkey   (str   "endkey=\"" endkey   "\""))
        connstr (str (server-db) "_design/osmcouch/_view/" source "?" skstr "&" ekstr)]
    (client/with-connection-pool {:default-per-route 1000 :threads 100}
      (-> (client/get connstr)
          (:body)
          (json/read-str)
          (update-in ["rows"] complete-rows)))))

(defn query-ways-list [startkey endkey]
  (let [skstr (when startkey (str "startkey=[\"" startkey "\", 0]"))
        ekstr (when endkey   (str   "endkey=[\"" endkey   "\", 1]"))
        connstr (str (server-db) "_design/osmcouch/_list/ways/ways?" skstr "&" ekstr)]
    (client/with-connection-pool {}
      (-> (client/get connstr)
          (:body)
          (json/read-str)))))

(defmacro defleveled [name & level-paths]
  (letfn [(insert-level [lv [method path params responder]]
            (list method 
                  (str "/" lv path) 
                  params 
                  `(binding [*level* ~lv] ~responder)))
          (mk-leveled [current-level level-paths]
            (when-let [[item & rest] level-paths]
              (cond 
                (integer? item) (mk-leveled item rest)
                (list? item)    (cons (insert-level current-level item)
                                        (mk-leveled current-level rest)))))]
    `(defroutes ~name ~@(mk-leveled 1 level-paths))))

(defleveled geo-routes
  1
  (GET "/node/:nid"    [nid]    (query-coords nid))
  (GET "/ways"         []       (json/write-str (query-ways nil)))
  (GET "/ways/:wid"    [wid]    (json/write-str (query-ways wid)))
  (GET "/waysnc"       []       (json/write-str (query-ways-complete true nil nil)))
  (GET "/waysnc/:name" [name]   (json/write-str (query-ways-complete true name name)))
  (GET "/waysc"        []       (json/write-str (query-ways-complete false nil nil)))
  (GET "/waysc/:wid"   [wid]    (json/write-str (query-ways-complete false wid wid)))
  2
  (GET "/node/:nid"    [nid]    (query-coords nid))
  (GET "/ways"         []       (json/write-str (query-ways nil)))
  (GET "/ways/:wid"    [wid]    (json/write-str (query-ways wid)))
  (GET "/waysnc"       []       (json/write-str (query-ways-complete true nil nil)))
  (GET "/waysnc/:name" [name]   (json/write-str (query-ways-complete true name name)))
  (GET "/waysc"        []       (json/write-str (query-ways-list nil nil)))
  (GET "/waysc/:wid"   [wid]    (json/write-str (query-ways-list wid wid))))

(def app 
  (-> geo-routes
      wrap-content-type))

; (defn rand-plot []
;  (let [x (repeatedly 25 #(rand-int 100))
;	y (repeatedly 25 #(rand-int 100))]
;    (charts/emit-svg
;     (-> (charts/xy-plot :width 500 :height 500 :label-points? true)
;         (charts/add-points [x y] :transpose-data?? true)))))
;
;(defn sin-cos-plot []
;  (let [x (range -5 5 0.05)
;	y1 (map #(Math/cos %) x)
;	y2 (map #(Math/sin %) x)]
;    (charts/emit-svg
;     (-> (charts/xy-plot :width 450 :height 200
;			 :xmin -5 :xmax 5
;			 :ymin -1.5 :ymax 1.5)
;         (charts/add-points [x y1] :transpose-data?? true
;			    :size 1)
;         (charts/add-points [x y2] :transpose-data?? true
;			    :size 1
;			    :fill (svg/rgb 255 0 0))))))

;(defn complete-map []
;  (let [ways (for [row (get (query-ways-complete) "rows")]
;               (get row "value"))
;        all-coords (apply concat (for [way ways] (get way "nodes")))
;        xs         (map first all-coords)
;        ys         (map second all-coords)
;        attrs {"width"  "800"
;               "height" "600"
;               "viewBox" (str (apply min xs) " " (apply max ys) " " (apply max xs) " " (appl;;;;;;;;;;;;;;;y min ys))}
;        drawn-ways   (for [way ways] 
;                       (apply concat (for [[[x1 y1] [x2 y2]] (pairs (get way "nodes"))]
;                                       (line x1 y1 x2 y2 :stroke "blue" :stroke-width "2px");;;;;;;;;;;)))]
;                                        ;   ways))
;    (xml/emit (svg attrs (apply group drawn-ways)))))
;
;(defn test-map []
;  (let [attrs {"width" "200"
;               "height" "100"
;               "viewBox" "0 0 200 100"}]
;    (xml/emit (svg attrs
;                   (rect 20 20 160 60 
;                         :fill "limegreen" 
;                         :stroke "black"
;                         :stroke-width "2px")))))
;
;(defn pairs [elements]
;  (map #(vector %1 %2) elements (rest elements)))
