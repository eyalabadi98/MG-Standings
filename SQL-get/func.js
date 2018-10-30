var mysql      = require('mysql');
    
exports.handler = vandium.generic()
    .handler( (event, context, callback) => {
    console.log("Event: " , event)
    
    var connection = mysql.createConnection({
    host: "mgdb.csjdzcwr1lpk.us-east-1.rds.amazonaws.com",
    user: "mgdbun",
    password: "MaccabiGames",
    database: "mgdb"
    });
    connection.query('SELECT * FROM mgdb.sign', function (error, results, fields) {
       if (error){console.log("Error: " , error)}
    console.log(results)
    callback( null, results );
        
  });
}

// // console.log("Result: ",handler({sql: "select * from sign"}))
// // console.log(getResult({sql: "select * from sign"}))

// // // exports.handler = function(event, context, callback) {
// // async function handler(event) {
// //     var mysql = require('mysql');
// //     sqlCommand = event.sql
// //     var con = mysql.createConnection({
// //       host: "mgdb.csjdzcwr1lpk.us-east-1.rds.amazonaws.com",
// //       user: "mgdbun",
// //       password: "MaccabiGames",
// //       database: "mgdb"
// //     });
// //     resultQuery = {}
// //     con.connect(function(err) {
// //       if (err) throw err;
// //       con.query(sqlCommand, function (err, result, fields) {
// //         if (err) throw err;
// //         resultQuery = result
// //         // console.log(result);
// //         return callback(result)
    
// //       });
// //     });
// //     const response = {
// //         statusCode: 200,
// //         body: JSON.stringify('Hello from Lambda!')
// //     };
// //     // return resultQuery;
// // };

// var mysql = require('mysql');




// exports.handler = async function(event, context, callback) {
//         console.log("Event " , JSON.stringify(event))
//         console.log("Context " , JSON.stringify(context))
//         sql = event.body
//         console.log("Request is " , sql)
//         context.callbackWaitsForEmptyEventLoop = false; 
//         var connection = mysql.createConnection({
//           host: "mgdb.csjdzcwr1lpk.us-east-1.rds.amazonaws.com",
//           user: "mgdbun",
//           password: "MaccabiGames",
//           database: "mgdb"
//         });
//         connection.query(sql, function (error, results, fields) {
//         if (error) {
//             connection.destroy();
//             console.log("Error " , error)
//             throw error;
//         } else {
//             // connected!
//             console.log("Results " ,results);
//             // callback(error, results);
//             connection.end(function (err) { 
//                 return false
//                 // callback(err, results);
            
//             });
//         }
//     });

// }

//         // con.connect();
//         // con.query(event.body, function(err, rows, fields) {
//         //     if (err) {console.log("Error " , err)}
//         //     console.log("rows: " + rows);
//         //     console.log("Done!")
//         //     rowsAll = rows
//         //     context.succeed('Success');
//         //     return rows
//         // });
//         // console.log("Done!", rowsAll)

//     // };

//     // sqlQuery = ""

//     // // sqlQuery = JSON.parse(event.body)
//     // // console.log("Event is " , sqlQuery.body)
//     // sqlQuery = JSON.stringify(event.body)
//     // console.log(sqlQuery)
//     // var connection = {
//     //     host: "mgdb.csjdzcwr1lpk.us-east-1.rds.amazonaws.com",
//     //     user: "mgdbun",
//     //     password: "MaccabiGames",
//     //     database: "mgdb"
//     //   };
//     // try {
    
//     //     connection = await mysql.createConnection(connection);
//     //     const result = await connection.query(event.body);
//     //     console.log(result[0]);
//     //     result = {}
//     //     var response = {
//     //         statusCode: 200,
//     //         body: result
//     //     };
//     //     return response;
  

//     // } finally {
//     //   if (connection && connection.end) connection.end();
//     // }

// // }