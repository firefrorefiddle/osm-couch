import io.plasmap.model.OsmObject
import com.ibm.couchdb._

trait Behaviour {
  def init(couch: CouchDb, db: Database) {}
  def see(obj: OsmObject)
  def postProcess() {}
}
