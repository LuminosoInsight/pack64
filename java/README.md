## Pack64 Java

### To compile

javac src/com/luminoso/pack64/*.java

### To run unit tests
Download junit jar
Download hamcrest jar

### To setup your build/test classpath environment

First Set up your classpath
```
CLASSPATH=.:./src:./test:./junit-4.13-beta-3.jar:./hamcrest-2.1.jar
export CLASSPATH
```
To compile the project
```
javac test/com/luminoso/pack64/*.java
javac src/com/luminoso/pack64/*.java
```
To run the unit tests:
```
java com.luminoso.pack64.Pack64Test
```
