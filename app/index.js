const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200);
    res.end('OK');
    return;
  }
  res.writeHead(200);
  res.end('Hello from ECS! Version: ' + (process.env.APP_VERSION || '1.0'));
});

server.listen(3000, () => console.log('Running on port 3000'));
