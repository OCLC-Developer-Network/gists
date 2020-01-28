# getOrder.bal

An Oauth2 authentication example using only the open source Ballerina.io integration language and no additional libraries or other external dependencies.
 
The code will consume purchaseOrder data from the WMS Acquisitions REST API
and select elements from the XML - both with and without the  `purchaseOrder` namespace - using the Ballerina `xml` primitive data type.

### Ballerina

"Ballerina is a general purpose, concurrent and strongly typed programming language with textual and graphical syntaxes, optimized for integration."

### Install and run the example:

1. Download and install the current Ballerina release from: https://ballerina.io/downloads.
2. Clone or download the getOrder.bal source file.
3. Fill in WSKey, Secret, and DataCenter prefix in getOrder.bal. (marked as TODO)
4. If using your own WMS instance instead of the public sandbox fill in an existing WMS orderNumber  in the `main` function.
5. From the directory containing the example compile and run the code using: `ballerina run getOrder.bal`.

### Improvements

To keep things simple all the code is in one file. One of the first improvements to consider would be to break out credentials and configuration into a separate file. Ballerina's built in Config library makes this very easy. E.g: `config:getAsString("keyStore.password")`.

Or may be you want to send WMS order data into your message queue. Just add `import ballerina/rabbitmq;` and you can set up a connection to RabbitMQ with `rabbitmq:Connection connection = new({ host: "rabbitmq.example.com", port: 5672 });`
