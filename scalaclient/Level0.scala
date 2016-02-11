import io.plasmap.model.OsmObject

object Level0 extends Behaviour {
  def see(obj: OsmObject) {
    println(obj)
  }
}
