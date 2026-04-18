const ExcelJS = require('exceljs');

async function test() {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile('大安区中小学校计算机终端设备统计表.xlsx');
    const worksheet = workbook.worksheets[0];
    
    // Original rows: 15
    // Row 3 is the first data row.
    // Let's duplicate row 3 for 5 data items.
    
    const dbData = [
        { device_type: 'PC1', brand_model: 'Brand A', config: 'i5/8G', mac: 'mac1', year: '2020', user: 'u1' },
        { device_type: 'PC2', brand_model: 'Brand B', config: 'i7/16G', mac: 'mac2', year: '2021', user: 'u2' },
        { device_type: 'PC3', brand_model: 'Brand C', config: 'i3/4G', mac: 'mac3', year: '2022', user: 'u3' }
    ];
    
    // We want to remove the existing sample rows 4 to 13. That is 10 rows.
    worksheet.spliceRows(4, 10); 
    // Now row 3 is the template data row.
    // row 4 is "……"
    // row 5 is "注：..."
    
    // Duplicate row 3 (which moves row 4, 5 down)
    worksheet.duplicateRow(3, dbData.length - 1, true); // true = insert
    
    // Fill data
    for (let i = 0; i < dbData.length; i++) {
        const row = worksheet.getRow(3 + i);
        const item = dbData[i];
        row.values = [
            null,
            i + 1,
            item.device_type,
            item.brand_model,
            item.config,
            item.mac,
            item.year,
            item.user,
            "" // 备注
        ];
    }
    
    await workbook.xlsx.writeFile('test_out.xlsx');
    console.log("Done");
}

test().catch(console.error);