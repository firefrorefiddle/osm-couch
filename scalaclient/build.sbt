scalaVersion := "2.11.6"

resolvers += "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots"

libraryDependencies += "io.plasmap" %% "geow" % "0.3.17-SNAPSHOT"

resolvers += "Oracle Downloads" at "http://download.oracle.com/maven"

libraryDependencies += "com.sleepycat" % "je" % "6.4.25"

libraryDependencies += "com.ibm" %% "couchdb-scala" % "0.6.0"
