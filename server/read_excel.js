const xlsx = require('xlsx');
const fs = require('fs');

const workbook = xlsx.readFile('大安区中小学校计算机终端设备统计表.xlsx');
const sheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[sheetName];
const data = xlsx.utils.sheet_to_json(worksheet, { header: 1 });

fs.writeFileSync('excel_data.json', JSON.stringify(data, null, 2), 'utf-8');
