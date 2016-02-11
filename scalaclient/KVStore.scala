import com.sleepycat.je._
import java.nio.file._
import java.io.File
import io.plasmap.model.OsmObject
import io.plasmap.serializer.OsmSerializer
import scala.util.{Try, Success, Failure}

class KVStore(filename: String) {
  
  val dir = Files.createTempDirectory(FileSystems.getDefault().getPath(".", "cache"),
				      filename)

  val db = 
    new Environment(dir.toFile, new EnvironmentConfig() setAllowCreate true).
    openDatabase(null, filename, new DatabaseConfig() setAllowCreate true)
  
  def _put(key: DatabaseEntry, data: DatabaseEntry) {
    db.put(null, key, data)
  }

  def put(key: String, data: OsmObject) = {
    _put(new DatabaseEntry(key.getBytes), new DatabaseEntry(OsmSerializer.toBinary(data)))
  }

  def get(key: String): Try[OsmObject] = {
    val out = new DatabaseEntry(null)
    val ret = db.get(null, new DatabaseEntry(key.getBytes), out, null)
    if(ret != OperationStatus.SUCCESS) {
      Failure(null)
    }
    else {
      OsmSerializer.fromBinary(out.getData)
    }
  }

  def close {
    db.close()
    db.getEnvironment().close()
  }
}
