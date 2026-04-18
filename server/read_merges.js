const xlsx = require('xlsx');
const workbook = xlsx.readFile('大安区中小学校计算机终端设备统计表.xlsx');
const sheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[sheetName];
console.log(JSON.stringify(worksheet['!merges'], null, 2));
