## Pack64 Java

    A Java version of the Pack64 library to encode and decode vectors into kind-of base64 format.

### To build

    mvn package

Maven will place the jar file in targets/Pack64-1.0.jar

### To run unit tests

    mvn tests

### To run the unit tests manually

    mvn dependency:copy-dependencies
    java -cp target/pack64-1.0.jar:target/test-classes:target/dependency/* com.luminoso.pack64.Pack64Test

