const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const cors = require('cors');
const ExcelJS = require('exceljs');

const app = express();
const PORT = 36867;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'data.db'), (err) => {
    if (err) {
        console.error('数据库连接失败:', err.message);
    } else {
        console.log('成功连接到 SQLite 数据库.');
        initDb();
    }
});

function initDb() {
    const createTableQuery = `
        CREATE TABLE IF NOT EXISTS devices (
            mac_address TEXT PRIMARY KEY,
            device_type TEXT,
            brand_model TEXT,
            cpu_info TEXT,
            ram_size TEXT,
            disk_size TEXT,
            screen_size TEXT,
            buy_year TEXT,
            user_name TEXT,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `;
    db.run(createTableQuery, (err) => {
        if (err) {
            console.error('创建表失败:', err.message);
        } else {
            console.log('数据表已准备就绪.');
        }
    });
}

// API: Report Device Info
app.post('/api/report', (req, res) => {
    const {
        mac_address,
        device_type,
        brand_model,
        cpu_info,
        ram_size,
        disk_size,
        screen_size,
        buy_year,
        user_name
    } = req.body;

    if (!mac_address) {
        return res.status(400).json({ success: false, message: 'MAC地址不能为空' });
    }

    const query = `
        INSERT INTO devices (
            mac_address, device_type, brand_model, cpu_info, 
            ram_size, disk_size, screen_size, buy_year, user_name, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(mac_address) DO UPDATE SET
            device_type = excluded.device_type,
            brand_model = excluded.brand_model,
            cpu_info = excluded.cpu_info,
            ram_size = excluded.ram_size,
            disk_size = excluded.disk_size,
            screen_size = excluded.screen_size,
            buy_year = excluded.buy_year,
            user_name = excluded.user_name,
            update_time = CURRENT_TIMESTAMP
    `;

    const params = [
        mac_address, device_type, brand_model, cpu_info,
        ram_size, disk_size, screen_size, buy_year, user_name
    ];

    db.run(query, params, function(err) {
        if (err) {
            console.error('保存数据失败:', err.message);
            return res.status(500).json({ success: false, message: '服务器内部错误' });
        }
        res.json({ success: true, message: '信息提交成功' });
    });
});

// API: Get All Devices
app.get('/api/devices', (req, res) => {
    db.all(`SELECT * FROM devices ORDER BY update_time DESC`, [], (err, rows) => {
        if (err) {
            console.error('查询数据失败:', err.message);
            return res.status(500).json({ success: false, message: '查询数据失败' });
        }
        res.json({ success: true, data: rows });
    });
});

// API: Export to Excel
app.get('/api/export', async (req, res) => {
    db.all(`SELECT * FROM devices ORDER BY update_time DESC`, [], async (err, rows) => {
        if (err) {
            console.error('查询数据失败:', err.message);
            return res.status(500).send('查询数据失败');
        }

        try {
            const workbook = new ExcelJS.Workbook();
            const templatePath = path.join(__dirname, '大安区中小学校计算机终端设备统计表.xlsx');
            await workbook.xlsx.readFile(templatePath);
            const worksheet = workbook.worksheets[0];

            // 模板中，前2行是标题和表头，第3行开始是数据示例，到第13行。
            // 我们保留第3行作为样式模板，删除第4行到第13行（共10行）
            worksheet.spliceRows(4, 10);

            if (rows.length === 0) {
                worksheet.getRow(3).values = ['', '', '', '', '', '', '', ''];
            } else {
                if (rows.length > 1) {
                    // 复制第3行（插入新行），保留样式
                    worksheet.duplicateRow(3, rows.length - 1, true);
                }

                // 填充数据
                for (let i = 0; i < rows.length; i++) {
                    const rowData = rows[i];
                    const row = worksheet.getRow(3 + i);
                    
                    // 按照模板格式拼接配置: CPU信息/内存(G)G/硬盘总大小(G)G/屏幕尺寸″
                    const configStr = `${rowData.cpu_info || ''}/${rowData.ram_size || '0'}G/${rowData.disk_size || '0'}G/${rowData.screen_size || ''}″`;
                    
                    // 在 ExcelJS 中，如果赋值的是数组，索引 0 会被忽略（因为列是从 1 开始的），
                    // 但有些情况下直接赋值数组也会让索引 0 映射到第一列，这取决于 API 版本的细微差异。
                    // 为了绝对安全和精准对应列，我们逐列赋值：
                    row.getCell(1).value = i + 1;                   // A列: 序号
                    row.getCell(2).value = rowData.device_type || ''; // B列: 设备类型
                    row.getCell(3).value = rowData.brand_model || ''; // C列: 品牌型号
                    row.getCell(4).value = configStr;               // D列: 基本配置
                    row.getCell(5).value = rowData.mac_address || ''; // E列: MAC地址
                    row.getCell(6).value = rowData.buy_year || '';    // F列: 采购年份
                    row.getCell(7).value = rowData.user_name || '';   // G列: 使用人
                    row.getCell(8).value = '';                       // H列: 备注
                }
            }

            res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
            res.setHeader('Content-Disposition', 'attachment; filename="devices_statistics.xlsx"');
            
            await workbook.xlsx.write(res);
            res.end();
        } catch (error) {
            console.error('导出Excel失败:', error);
            res.status(500).send('导出Excel失败');
        }
    });
});

// Start Server
app.listen(PORT, () => {
    console.log(`服务端正在运行, 访问地址: http://localhost:${PORT}`);
});
