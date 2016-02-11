case class Config (serverURL: String,
		   serverPort: Int,
		   dbName: String,
		   behaviour: Behaviour)

object Config {
  dev level0 = Config("localhost",
		      5984,
		      "saalfelden_0",
		      Level0)
}
