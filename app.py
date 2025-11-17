"""Flask web application for StrmConvert."""
from flask import Flask, render_template_string, request, jsonify
from config_manager import ConfigManager
from watchdog_monitor import WatchdogMonitor
import threading

app = Flask(__name__)
config_manager = ConfigManager()
monitor = WatchdogMonitor()

# HTML Templates
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrmConvert - 控制面板</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --bs-body-bg: #1a1a1a;
            --bs-body-color: #e0e0e0;
            --bs-card-bg: #2d2d2d;
            --bs-card-border-color: #404040;
            --bs-border-color: #404040;
            --bs-table-bg: #2d2d2d;
            --bs-table-striped-bg: #353535;
            --bs-table-hover-bg: #3d3d3d;
            --bs-modal-bg: #2d2d2d;
            --bs-modal-header-border-color: #404040;
            --bs-input-bg: #353535;
            --bs-input-border-color: #505050;
            --bs-input-color: #e0e0e0;
            --bs-input-focus-bg: #3d3d3d;
            --bs-input-focus-border-color: #6c757d;
            --bs-dropdown-bg: #2d2d2d;
            --bs-dropdown-link-color: #e0e0e0;
            --bs-dropdown-link-hover-bg: #3d3d3d;
        }
        
        body {
            background-color: var(--bs-body-bg);
            color: var(--bs-body-color);
        }
        
        .card {
            margin-bottom: 1rem;
            background-color: var(--bs-card-bg);
            border-color: var(--bs-card-border-color);
            color: var(--bs-body-color);
        }
        
        .card-header {
            background-color: var(--bs-card-bg);
            border-bottom-color: var(--bs-card-border-color);
        }
        
        .table {
            color: var(--bs-body-color);
        }
        
        .table-striped > tbody > tr:nth-of-type(odd) > td {
            background-color: var(--bs-table-striped-bg);
        }
        
        .table-hover > tbody > tr:hover > td {
            background-color: var(--bs-table-hover-bg);
        }
        
        .modal-content {
            background-color: var(--bs-modal-bg);
            color: var(--bs-body-color);
        }
        
        .modal-header {
            border-bottom-color: var(--bs-modal-header-border-color);
        }
        
        .modal-footer {
            border-top-color: var(--bs-modal-header-border-color);
        }
        
        .form-control {
            background-color: var(--bs-input-bg);
            border-color: var(--bs-input-border-color);
            color: var(--bs-input-color);
        }
        
        .form-control:focus {
            background-color: var(--bs-input-focus-bg);
            border-color: var(--bs-input-focus-border-color);
            color: var(--bs-input-color);
        }
        
        .form-control::placeholder {
            color: #999;
        }
        
        .form-label {
            color: var(--bs-body-color);
        }
        
        .form-text {
            color: #999;
        }
        
        .dropdown-menu {
            background-color: var(--bs-dropdown-bg);
            border-color: var(--bs-card-border-color);
        }
        
        .dropdown-item {
            color: var(--bs-dropdown-link-color);
        }
        
        .dropdown-item:hover {
            background-color: var(--bs-dropdown-link-hover-bg);
            color: var(--bs-body-color);
        }
        
        .dropdown-divider {
            border-top-color: var(--bs-card-border-color);
        }
        
        code {
            background-color: #1a1a1a;
            color: #ff6b9d;
        }
        
        .text-muted {
            color: #999 !important;
        }
        
        .toast {
            background-color: var(--bs-card-bg);
            border-color: var(--bs-card-border-color);
        }
        
        .toast-body {
            color: var(--bs-body-color);
        }
        
        .status-badge { font-size: 0.9em; }
        .btn-sm { padding: 0.2rem 0.4rem; font-size: 0.875rem; }
        .btn-group .btn-sm { padding: 0.2rem 0.4rem; }
        .table td { padding: 0.5rem; }
        .table td:nth-last-child(-n+2) { 
            padding: 0.3rem 0.4rem; 
            white-space: nowrap;
            width: 1%;
        }
        .table td:nth-last-child(-n+2) .btn-sm {
            margin-right: 0.25rem;
        }
        .table td:nth-last-child(-n+2) .btn-sm:last-child {
            margin-right: 0;
        }
        h1 {
            font-size: 1.75rem;
        }
        
        /* Control panel button consistency */
        .card-header > div {
            display: flex;
            align-items: center;
        }
        
        .card-header > div > .btn {
            min-width: 100px;
            flex: 0 0 auto;
        }
        
        /* Mobile card layout */
        .mobile-cards {
            display: none;
        }
        
        .mobile-card {
            border: 1px solid var(--bs-card-border-color);
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: var(--bs-card-bg);
        }
        
        .mobile-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--bs-card-border-color);
        }
        
        .mobile-card-body {
            margin-bottom: 0.75rem;
        }
        
        .mobile-card-body-item {
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        
        .mobile-card-body-item strong {
            display: inline-block;
            min-width: 80px;
            color: #6c757d;
        }
        
        .mobile-card-actions {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .mobile-card-actions .btn {
            width: 100%;
        }
        
        .mobile-card-actions-row {
            display: flex;
            gap: 0.5rem;
            width: 100%;
        }
        
        .mobile-card-actions-row .btn {
            flex: 1 1 0;
            min-width: 0;
            width: 0;
        }
        
        .mobile-card-actions .btn-group {
            width: 100%;
        }
        
        .mobile-card-actions .btn-group .btn {
            width: 100%;
        }
        
        /* Mobile responsive styles */
        @media (max-width: 768px) {
            .table-responsive {
                display: none !important;
            }
            .mobile-cards {
                display: block;
            }
            .btn-sm {
                padding: 0.5rem 0.75rem;
                font-size: 0.875rem;
                min-height: 44px; /* Better touch target */
            }
            .card-header {
                flex-wrap: wrap;
                justify-content: center !important;
            }
            .card-header > div {
                width: 100%;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 0.5rem;
            }
            .card-header .btn {
                flex: 1 1 auto;
                min-width: calc(33.333% - 0.334rem);
                max-width: 200px;
            }
            h1 {
                font-size: 1.5rem;
            }
            code {
                font-size: 0.8rem;
                word-break: break-all;
                display: block;
                padding: 0.25rem;
                background-color: #1a1a1a;
                border-radius: 0.25rem;
                color: #ff6b9d;
            }
        }
        
        @media (min-width: 769px) {
            .mobile-cards {
                display: none !important;
            }
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">StrmConvert 控制面板</h1>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-end align-items-center">
                        <div>
                            <button id="btnStartAll" class="btn btn-success btn-sm me-2" onclick="startAll()">全部启动</button>
                            <button id="btnStopAll" class="btn btn-danger btn-sm me-2" onclick="stopAll()">全部停止</button>
                            <button class="btn btn-primary btn-sm" onclick="syncAll()">全部同步</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-2">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <div id="recordsList"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Container -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1055;">
    </div>
    
    <!-- Config Modal -->
    <div class="modal fade" id="configModal" tabindex="-1" aria-labelledby="configModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="configModalLabel">配置记录</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
                </div>
                <div class="modal-body">
                    <form id="configForm" onsubmit="event.preventDefault(); saveRecordConfig();">
                        <div class="mb-3">
                            <label for="configSourceFolder" class="form-label">源文件夹 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="configSourceFolder" 
                                   placeholder="/path/to/source" required>
                            <small class="form-text text-muted">包含 .strm 文件的文件夹路径</small>
                        </div>
                        <div class="mb-3">
                            <label for="configTargetFolder" class="form-label">目标文件夹 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="configTargetFolder" 
                                   placeholder="/path/to/target" required>
                            <small class="form-text text-muted">转换后文件保存的路径</small>
                        </div>
                        <div class="mb-3">
                            <label for="configSearchString" class="form-label">搜索字符串</label>
                            <input type="text" class="form-control" id="configSearchString" 
                                   placeholder="/old/path (留空表示仅同步，不转换)">
                            <small class="form-text text-muted">在 .strm 文件中要搜索的字符串（留空表示仅同步，不转换）</small>
                        </div>
                        <div class="mb-3">
                            <label for="configReplacementString" class="form-label">替换字符串</label>
                            <input type="text" class="form-control" id="configReplacementString" 
                                   placeholder="/new/path (留空表示仅同步，不转换)">
                            <small class="form-text text-muted">用于替换搜索字符串的字符串（留空表示仅同步，不转换）</small>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                    <button type="button" class="btn btn-primary" onclick="saveRecordConfig()">保存</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let statusInterval;
        let currentEditingRecordId = null;
        let allRecords = [];
        let allStatus = {};
        
        function showMessage(message, type) {
            const toastContainer = document.querySelector('.toast-container');
            const toastId = 'toast-' + Date.now();
            
            // Map type to Bootstrap toast classes
            const bgClass = type === 'success' ? 'bg-success' : 
                           type === 'danger' ? 'bg-danger' : 
                           type === 'warning' ? 'bg-warning' : 
                           'bg-info';
            
            const typeLabel = type === 'success' ? '成功' : 
                            type === 'danger' ? '错误' : 
                            type === 'warning' ? '警告' : 
                            '信息';
            
            const toastHtml = `
                <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header ${bgClass} text-white">
                        <strong class="me-auto">${typeLabel}</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="关闭"></button>
                    </div>
                    <div class="toast-body">
                        ${escapeHtml(message)}
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: 3000
            });
            toast.show();
            
            // Remove toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const recordsList = document.getElementById('recordsList');
                    const status = data.status || {};
                    allRecords = data.records || [];
                    allStatus = status;
                    
                    if (allRecords.length > 0) {
                        // Desktop table view
                        let tableHtml = '<div class="table-responsive"><table class="table table-striped"><tbody>';
                        // Mobile card view
                        let cardHtml = '<div class="mobile-cards">';
                        
                        allRecords.forEach((record, idx) => {
                            const recordId = record.id || '';
                            const isMonitoring = status[recordId] || false;
                            const statusBadge = isMonitoring 
                                ? '<span class="badge bg-success">监控中</span>' 
                                : '<span class="badge bg-secondary">已停止</span>';
                            
                            // Table row for desktop
                            tableHtml += `<tr>
                                <td>${idx}</td>
                                <td><code>${escapeHtml(record.source_folder)}</code></td>
                                <td><code>${escapeHtml(record.target_folder)}</code></td>
                                <td>${statusBadge}</td>
                                <td>
                                    ${isMonitoring 
                                        ? `<button class="btn btn-sm btn-warning me-1" onclick="toggleWatch('${recordId}', false)">停止监控</button>`
                                        : `<button class="btn btn-sm btn-success me-1" onclick="toggleWatch('${recordId}', true)">启动监控</button>`
                                    }
                                    <button class="btn btn-sm btn-primary" onclick="syncRecord('${recordId}')">全量同步</button>
                                </td>
                                <td style="text-align: right;">
                                    <button class="btn btn-sm btn-info me-1" onclick="openConfigDialog('${recordId}')" title="配置">
                                        <i class="bi bi-gear"></i> 配置
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteRecord('${recordId}')" title="删除">
                                        <i class="bi bi-trash"></i> 删除
                                    </button>
                                </td>
                            </tr>`;
                            
                            // Card for mobile
                            cardHtml += `<div class="mobile-card">
                                <div class="mobile-card-header">
                                    <span><strong>记录 #${idx}</strong> ${statusBadge}</span>
                                </div>
                                <div class="mobile-card-body">
                                    <div class="mobile-card-body-item">
                                        <strong>源文件夹:</strong>
                                        <code>${escapeHtml(record.source_folder)}</code>
                                    </div>
                                    <div class="mobile-card-body-item">
                                        <strong>目标文件夹:</strong>
                                        <code>${escapeHtml(record.target_folder)}</code>
                                    </div>
                                </div>
                                <div class="mobile-card-actions">
                                    <div class="mobile-card-actions-row">
                                        ${isMonitoring 
                                            ? `<button class="btn btn-sm btn-warning" onclick="toggleWatch('${recordId}', false)">停止监控</button>`
                                            : `<button class="btn btn-sm btn-success" onclick="toggleWatch('${recordId}', true)">启动监控</button>`
                                        }
                                        <button class="btn btn-sm btn-primary" onclick="syncRecord('${recordId}')">全量同步</button>
                                    </div>
                                    <div class="mobile-card-actions-row">
                                        <button class="btn btn-sm btn-info" onclick="openConfigDialog('${recordId}')" title="配置">
                                            <i class="bi bi-gear"></i> 配置
                                        </button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteRecord('${recordId}')" title="删除">
                                            <i class="bi bi-trash"></i> 删除
                                        </button>
                                    </div>
                                </div>
                            </div>`;
                        });
                        
                        tableHtml += '</tbody></table></div>';
                        cardHtml += '</div>';
                        
                        let html = tableHtml + cardHtml;
                        html += '<div class="mt-3 text-end"><button class="btn btn-outline-primary btn-sm" onclick="addNewRecord()"><i class="bi bi-plus-circle"></i> 添加新记录</button></div>';
                        recordsList.innerHTML = html;
                    } else {
                        recordsList.innerHTML = '<p class="text-muted text-center">暂无配置记录。 <button class="btn btn-sm btn-primary" onclick="addNewRecord()">添加一个</button></p>';
                    }
                })
                .catch(err => console.error('Error:', err));
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function openConfigDialog(recordId) {
            currentEditingRecordId = recordId;
            // Find record by UUID
            const record = allRecords.find(r => r.id === recordId);
            
            if (record) {
                // Editing existing record
                document.getElementById('configSourceFolder').value = record.source_folder || '';
                document.getElementById('configTargetFolder').value = record.target_folder || '';
                document.getElementById('configSearchString').value = record.search_string || '';
                document.getElementById('configReplacementString').value = record.replacement_string || '';
                const recordIndex = allRecords.findIndex(r => r.id === recordId);
                document.getElementById('configModalLabel').textContent = `配置记录 #${recordIndex}`;
            } else {
                // New record
                document.getElementById('configSourceFolder').value = '';
                document.getElementById('configTargetFolder').value = '';
                document.getElementById('configSearchString').value = '';
                document.getElementById('configReplacementString').value = '';
                document.getElementById('configModalLabel').textContent = '添加新记录';
            }
            
            const modal = new bootstrap.Modal(document.getElementById('configModal'));
            modal.show();
        }
        
        function addNewRecord() {
            // Use 'new' as placeholder ID - backend will generate UUID
            currentEditingRecordId = 'new';
            openConfigDialog('new');
        }
        
        function saveRecordConfig() {
            const record = {
                source_folder: document.getElementById('configSourceFolder').value.trim(),
                target_folder: document.getElementById('configTargetFolder').value.trim(),
                search_string: document.getElementById('configSearchString').value.trim(),
                replacement_string: document.getElementById('configReplacementString').value.trim()
            };
            
            // Validate (only source_folder and target_folder are required)
            if (!record.source_folder || !record.target_folder) {
                showMessage('源文件夹和目标文件夹是必填项', 'danger');
                return;
            }
            // search_string and replacement_string can be empty (for sync without conversion)
            // They are always strings (even if empty) after trim(), so no additional validation needed
            
            // Save the record
            fetch(`/api/config/record/${currentEditingRecordId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ record: record })
            })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showMessage('记录已保存成功', 'success');
                        // Close modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('configModal'));
                        modal.hide();
                        
                        // Refresh status first
                        updateStatus();
                        
                        // Get the actual record ID from response (for new records, this will be the generated UUID)
                        const actualRecordId = data.record_id || currentEditingRecordId;
                        
                        // If it was monitoring, restart it
                        if (data.was_monitoring) {
                            setTimeout(() => {
                                fetch('/api/watch/start', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ record_id: actualRecordId })
                                })
                                    .then(r => r.json())
                                    .then(data => {
                                        if (data.success) {
                                            showMessage('记录已保存并重新启动监控', 'success');
                                        } else {
                                            showMessage('记录已保存但重新启动监控失败', 'warning');
                                        }
                                        updateStatus();
                                    })
                                    .catch(err => {
                                        showMessage('记录已保存但重新启动监控失败', 'warning');
                                        updateStatus();
                                    });
                            }, 500);
                        }
                    } else {
                        showMessage('错误: ' + (data.message || '保存失败'), 'danger');
                    }
                })
                .catch(err => {
                    showMessage('错误: ' + err, 'danger');
                });
        }
        
        function startAll() {
            fetch('/api/watch/start', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message || '已启动所有监控', data.success ? 'success' : 'danger');
                    updateStatus();
                });
        }
        
        function stopAll() {
            fetch('/api/watch/stop', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message || '已停止所有监控', data.success ? 'success' : 'danger');
                    updateStatus();
                });
        }
        
        function syncAll() {
            fetch('/api/sync', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        if (data.stats) {
                            const stats = data.stats;
                            showMessage(`同步完成：创建: ${stats.created || 0}, 更新: ${stats.updated || 0}, 删除: ${stats.deleted || 0}, 错误: ${stats.errors || 0}`, 'success');
                        } else {
                            showMessage(data.message || '同步完成', 'success');
                        }
                    } else {
                        showMessage(data.message || '同步完成', 'danger');
                    }
                });
        }
        
        function syncRecord(recordId) {
            fetch(`/api/sync/${recordId}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message || '同步完成', data.success ? 'success' : 'danger');
                    if (data.stats) {
                        const stats = data.stats;
                        showMessage(`同步: 创建: ${stats.created || 0}, 更新: ${stats.updated || 0}, 删除: ${stats.deleted || 0}, 错误: ${stats.errors || 0}`, 'info');
                    }
                    updateStatus();
                });
        }
        
        function toggleWatch(recordId, start) {
            const endpoint = start ? '/api/watch/start' : '/api/watch/stop';
            fetch(endpoint, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ record_id: recordId })
            })
                .then(r => r.json())
                .then(data => {
                    showMessage(data.message || (start ? '已启动' : '已停止'), data.success ? 'success' : 'danger');
                    updateStatus();
                });
        }
        
        function deleteRecord(recordId) {
            if (!confirm('确定要删除此记录吗？')) {
                return;
            }
            
            fetch(`/api/config/record/${recordId}`, { method: 'DELETE' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showMessage('记录已删除', 'success');
                        updateStatus();
                    } else {
                        showMessage('删除失败: ' + (data.message || '未知错误'), 'danger');
                    }
                })
                .catch(err => {
                    showMessage('删除失败: ' + err, 'danger');
                });
        }
        
        // Update status every 2 seconds
        statusInterval = setInterval(updateStatus, 2000);
        updateStatus();
        
        // Listen for storage events (when config is saved from another tab/window)
        window.addEventListener('storage', function(e) {
            if (e.key === 'configUpdated') {
                updateStatus();
            }
        });
        
        // Also check for config updates via polling (in case storage events don't work)
        let lastConfigHash = null;
        setInterval(function() {
            fetch('/api/config')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const currentHash = JSON.stringify(data.config);
                        if (lastConfigHash && lastConfigHash !== currentHash) {
                            updateStatus();
                        }
                        lastConfigHash = currentHash;
                    }
                })
                .catch(() => {});
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Dashboard page."""
    return render_template_string(DASHBOARD_TEMPLATE)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    try:
        config = config_manager.load()
        # Also provide YAML string for easier editing
        import yaml
        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return jsonify({'success': True, 'config': config, 'yaml': yaml_str})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration."""
    try:
        data = request.get_json()
        if 'yaml' in data:
            # Parse YAML string
            import yaml
            config = yaml.safe_load(data['yaml'])
        elif 'config' in data:
            config = data['config']
        else:
            return jsonify({'success': False, 'message': '无效请求'}), 400
        
        # Validate configuration
        is_valid, error_msg = config_manager.validate(config)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Stop all current observers before updating config
        # This prevents conflicts with old configuration
        monitor.stop_all()
        
        # Save configuration
        config_manager.save(config)
        
        # Reload config to ensure it's fresh
        config_manager.load()
        
        return jsonify({
            'success': True, 
            'message': 'Configuration saved. All monitoring has been stopped. Please restart monitoring if needed.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/config/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a configuration record."""
    try:
        # Load current config
        config = config_manager.load()
        records = config.get('records', [])
        
        # Find and remove the record
        record = config_manager.get_record_by_id(record_id)
        if record is None:
            return jsonify({'success': False, 'message': '记录不存在'}), 404
        
        # Stop monitoring if it's running
        if monitor.is_monitoring(record_id):
            monitor.stop_monitoring(record_id)
        
        # Remove the record
        records = [r for r in records if r.get('id') != record_id]
        config['records'] = records
        
        # Validate the entire config
        is_valid, error_msg = config_manager.validate(config)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Save configuration
        config_manager.save(config)
        
        # Reload config to ensure it's fresh
        config_manager.load()
        
        return jsonify({
            'success': True,
            'message': '记录已删除'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/config/record/<record_id>', methods=['POST'])
def update_record(record_id):
    """Update a single configuration record."""
    try:
        data = request.get_json()
        if 'record' not in data:
            return jsonify({'success': False, 'message': '无效请求：缺少记录'}), 400
        
        new_record = data['record']
        
        # Validate record fields
        # source_folder and target_folder are required and cannot be empty
        if 'source_folder' not in new_record or not isinstance(new_record['source_folder'], str) or not new_record['source_folder'].strip():
            return jsonify({'success': False, 'message': 'Missing or invalid field: source_folder'}), 400
        if 'target_folder' not in new_record or not isinstance(new_record['target_folder'], str) or not new_record['target_folder'].strip():
            return jsonify({'success': False, 'message': 'Missing or invalid field: target_folder'}), 400
        # search_string and replacement_string are required but can be empty (for sync without conversion)
        if 'search_string' not in new_record or not isinstance(new_record['search_string'], str):
            return jsonify({'success': False, 'message': 'Missing or invalid field: search_string'}), 400
        if 'replacement_string' not in new_record or not isinstance(new_record['replacement_string'], str):
            return jsonify({'success': False, 'message': 'Missing or invalid field: replacement_string'}), 400
        
        # Load current config
        config = config_manager.load()
        records = config.get('records', [])
        
        # Check if this is a new record (record_id is 'new' or doesn't exist) or updating existing
        existing_record = None
        if record_id != 'new':
            existing_record = config_manager.get_record_by_id(record_id)
        
        if existing_record is None or record_id == 'new':
            # Add new record - generate UUID
            import uuid
            new_record['id'] = str(uuid.uuid4())
            records.append(new_record)
            was_monitoring = False
        else:
            # Update existing record - preserve UUID and check if monitoring was active
            new_record['id'] = record_id
            was_monitoring = monitor.is_monitoring(record_id)
            
            # Stop monitoring if it was running
            if was_monitoring:
                monitor.stop_monitoring(record_id)
            
            # Update the record in the list
            record_idx = config_manager.get_record_index(record_id)
            if record_idx is not None:
                records[record_idx] = new_record
        
        # Validate the entire config
        config['records'] = records
        is_valid, error_msg = config_manager.validate(config)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Save configuration
        config_manager.save(config)
        
        # Reload config to ensure it's fresh
        config_manager.load()
        
        return jsonify({
            'success': True,
            'message': '记录已保存成功',
            'record_id': new_record['id'],
            'was_monitoring': was_monitoring
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get monitoring status."""
    try:
        config = config_manager.load()
        status = monitor.get_status()
        return jsonify({
            'success': True,
            'records': config.get('records', []),
            'status': status
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/sync', methods=['POST'])
def sync_all():
    """Perform full sync for all records."""
    try:
        config = config_manager.load()
        records = config.get('records', [])
        
        total_stats = {'created': 0, 'updated': 0, 'deleted': 0, 'errors': 0}
        
        for idx, record in enumerate(records):
            from folder_sync import FolderSync
            folder_sync = FolderSync(
                record['source_folder'],
                record['target_folder'],
                record['search_string'],
                record['replacement_string']
            )
            stats = folder_sync.sync_all()
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)
        
        return jsonify({
            'success': True,
            'message': '同步完成',
            'stats': total_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/sync/<record_id>', methods=['POST'])
def sync_record(record_id):
    """Perform full sync for a specific record."""
    try:
        stats = monitor.sync_record(record_id)
        if stats is None:
            # Record not in monitor, create temporary sync
            record = config_manager.get_record_by_id(record_id)
            if record is None:
                return jsonify({'success': False, 'message': '无效的记录ID'}), 400
            
            from folder_sync import FolderSync
            folder_sync = FolderSync(
                record['source_folder'],
                record['target_folder'],
                record['search_string'],
                record['replacement_string']
            )
            stats = folder_sync.sync_all()
        
        return jsonify({
            'success': True,
            'message': '同步完成',
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/watch/start', methods=['POST'])
def start_watch():
    """Start monitoring."""
    try:
        data = request.get_json() or {}
        record_id = data.get('record_id')
        
        config = config_manager.load()
        records = config.get('records', [])
        
        if record_id is not None:
            # Start specific record
            record = config_manager.get_record_by_id(record_id)
            if record is None:
                return jsonify({'success': False, 'message': '无效的记录ID'}), 400
            
            success = monitor.start_monitoring(
                record_id,
                record['source_folder'],
                record['target_folder'],
                record['search_string'],
                record['replacement_string']
            )
            if success:
                return jsonify({'success': True, 'message': '已启动监控记录'})
            else:
                return jsonify({'success': False, 'message': '启动监控失败'}), 500
        else:
            # Start all records
            started = 0
            for record in records:
                record_id = record.get('id')
                if record_id and monitor.start_monitoring(
                    record_id,
                    record['source_folder'],
                    record['target_folder'],
                    record['search_string'],
                    record['replacement_string']
                ):
                    started += 1
            
            return jsonify({
                'success': True,
                'message': f'已启动监控 {started}/{len(records)} 条记录'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/watch/stop', methods=['POST'])
def stop_watch():
    """Stop monitoring."""
    try:
        data = request.get_json() or {}
        record_id = data.get('record_id')
        
        if record_id is not None:
            # Stop specific record
            success = monitor.stop_monitoring(record_id)
            if success:
                return jsonify({'success': True, 'message': '已停止监控记录'})
            else:
                return jsonify({'success': False, 'message': '记录未在监控中'}), 400
        else:
            # Stop all records
            monitor.stop_all()
            return jsonify({'success': True, 'message': '已停止所有监控'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9115, debug=False)

