import io.plasmap.model.OsmObject

object SaveAll extends Behaviour {
  val dict = new KVStore("objects")

  def see(obj: OsmObject) {
    dict.put(obj.id.toString, obj)
  }

  override def postProcess {
    dict.close
  }
}
