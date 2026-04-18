const fs = require('fs');
const http = require('http');

http.get('http://localhost:36867/api/export', (res) => {
    const fileStream = fs.createWriteStream('test_download.xlsx');
    res.pipe(fileStream);
    fileStream.on('finish', () => {
        fileStream.close();
        console.log('Download complete');
    });
});