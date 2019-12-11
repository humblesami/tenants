var fs = require("fs");
var http = require("http");
const { exec } = require('child_process');
var express = require("express");
var app = express();
var public_path = __dirname + '/html';
public_path = express.static(public_path);
app.use(public_path);

function execute_child_process(res, cmd, callback, failure_cb) {
    try {
        exec(cmd, (err, data) => {
            if (err) {
                if (failure_cb)
                    failure_cb(res, err);
                else
                    res.send(err.message);
            } else {
                if (callback)
                    callback(res, data);
                else
                    res.send('Done');
            }
        });

    } catch (e) {
        res.send(e.message);
    }
}

app.get('/pull', function(req, res) {
    req = req.query;
    pull_code(req, res);
});
app.get('/push', function(req, res){
    req = req.query;
    var branch = req.branch;
    var remote = req.remote;
    var message = req.message;
    pull_code(req, res, function () {
        execute_child_process(res,'git add .', function(){
            execute_child_process(res,'git commit -m "'+message+'"', function(){
                execute_child_process(res,'git push origin '+branch, function(){
                    onGitDone(res, remote);
                });
            });
        });
    })
});

function onGitDone(res, remote)
{
    execute_child_process(res,'git remote set-url origin https://'+remote, function () {
        res.send('Done');
    });
}

function pull_code(req, res, callback)
{
    try{
        var username = req.uname;
        var password = req.password;
        var remote = req.remote;
        var branch = req.branch;

        if (username && password && remote && branch)
        {

        }
        else
        {
            res.send('Invalid input');
            return;
        }
        var remote_with_unp = 'https://'+username+':'+password+'@'+remote;

        execute_child_process(res,'git remote set-url origin '+remote_with_unp, on_remote_updated, on_remote_not_found);

        function on_remote_not_found(res) {
            execute_child_process(res,'git remote add origin '+remote_with_unp, on_remote_updated);
        }
        function on_remote_updated(res)
        {
            execute_child_process(res,'git pull origin '+branch, function () {
                if(callback)
                    callback(res);
                else
                {
                    onGitDone(res, remote);
                }
            });
        }
    }
    catch (er) {
        console.log(er);
        res.send(er.message)
    }
}



var webserver = http.createServer(app);
var server_port = 5001;
webserver.listen(server_port, "0.0.0.0");
console.log("Listening Git:" + server_port);
