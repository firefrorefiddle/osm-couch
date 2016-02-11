import io.plasmap.parser.OsmParser
import com.sleepycat.persist._

object Import extends App {
  
  def saalfelden = "../saalfelden.osm"
  def austria = "/home/mhartl/Downloads/austria-latest.osm.pbf"

  def run(config: Config) {

    val couch = CouchDB(config.serverUrl, config.serverPort)
    val db = couch.dbs.create(config.dbName)
    val beh = config.behaviour

    beh.init(couch, db)

    for (elem <- parser) elem match {
	case Some(obj) => beh.see(obj)
	case None => ;
    }

    beh.postProcess()
  }
  
  override def main(args: Array[String]) {    
    val parser = OsmParser(austria)
    run(Config.level0)
  }
}

