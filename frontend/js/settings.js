import { showToast } from './utils.js';

let previousMode = null;
let modelConfigs = null;
let providerConfigs = {};

// AI Provider configurations
const AI_PROVIDERS = {
    'deepseek': {
        name: 'DeepSeek',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true },
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'https://api.deepseek.com/v1' }
        ],
        models: ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']
    },
    'aliyun': {
        name: '阿里云通义千问',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true },
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'https://dashscope.aliyuncs.com/api/v1' }
        ],
        models: ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen2.5-72b-instruct', 'qwen2.5-32b-instruct', 'qwen2.5-14b-instruct', 'qwen2.5-7b-instruct']
    },
    'zhipuai': {
        name: '智谱AI',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true }
        ],
        models: ['glm-4-air', 'glm-4-flashx', 'glm-4-plus', 'glm-4v-plus', 'glm-4-0520', 'glm-4-long']
    },
    'lmstudio': {
        name: 'LM Studio',
        fields: [
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'http://localhost:1234/v1' },
            { key: 'api_key', label: 'API Key', type: 'text', default: 'lm-studio' }
        ],
        models: []  // Models will be dynamically loaded
    },
    'gemini': {
        name: 'Google Gemini',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true },
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'https://generativelanguage.googleapis.com' }
        ],
        models: ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-pro-exp', 'gemini-2.0-flash-exp']
    },
    'openrouter': {
        name: 'OpenRouter',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true },
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'https://openrouter.ai/api/v1' }
        ],
        models: []  // Models will be dynamically loaded
    },
    'claude': {
        name: 'Anthropic Claude',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'text', required: true },
            { key: 'base_url', label: 'Base URL', type: 'text', default: 'https://api.anthropic.com' }
        ],
        models: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
    }
};

// Create and append the settings popup HTML to the document
function createSettingsPopup() {
    const overlay = document.createElement('div');
    overlay.className = 'settings-overlay';
    
    const popup = document.createElement('div');
    popup.className = 'settings-popup settings-popup-large';
    
    // Get settings from localStorage
    const settings = JSON.parse(localStorage.getItem('settings') || '{}');
    const providerSettings = JSON.parse(localStorage.getItem('providerConfigs') || '{}');
    
    popup.innerHTML = `
        <div class="settings-header">
            <div class="header-content">
                <h3>高级设置</h3>
                <p class="subtitle">配置AI提供商、系统参数和模型选择</p>
            </div>
            <button class="settings-close">&times;</button>
        </div>
        <div class="settings-nav">
            <button class="settings-tab active" data-tab="providers">AI提供商</button>
            <button class="settings-tab" data-tab="models">模型设置</button>
            <button class="settings-tab" data-tab="system">系统设置</button>
            <button class="settings-tab" data-tab="prompts">提示词配置</button>
        </div>
        <div class="settings-content">
            <!-- AI提供商配置 -->
            <div class="settings-section active" data-section="providers">
                <div class="provider-config-container">
                    <div class="provider-selector">
                        <h4>选择AI提供商</h4>
                        <select id="providerSelect">
                            <option value="">选择提供商...</option>
                            ${Object.entries(AI_PROVIDERS).map(([key, provider]) => 
                                `<option value="${key}">${provider.name}</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="provider-config-form" id="providerConfigForm" style="display: none;">
                        <div class="config-form-content"></div>
                        <div class="config-actions">
                            <button class="test-connection-btn">🔍 测试连接</button>
                            <button class="save-provider-btn">💾 保存配置</button>
                            <button class="load-models-btn">📋 加载模型</button>
                        </div>
                        <div class="connection-status"></div>
                    </div>
                    <div class="configured-providers">
                        <h4>已配置的提供商</h4>
                        <div class="provider-list" id="configuredProvidersList"></div>
                    </div>
                </div>
            </div>
            
            <!-- 模型设置 -->
            <div class="settings-section" data-section="models">
                <h4>模型选择</h4>
                <div class="setting-item">
                    <label for="defaultMainModel">主模型</label>
                    <div class="model-select-group">
                        <select id="defaultMainModel"></select>
                        <button class="test-model-btn" data-for="defaultMainModel">测试</button>
                    </div>
                </div>
                <div class="setting-item">
                    <label for="defaultSubModel">辅助模型</label>
                    <div class="model-select-group">
                        <select id="defaultSubModel"></select>
                        <button class="test-model-btn" data-for="defaultSubModel">测试</button>
                    </div>
                </div>
                <div class="setting-item">
                    <button class="reload-models-btn">🔄 重新加载所有模型</button>
                </div>
            </div>
            
            <!-- 系统设置 -->
            <div class="settings-section" data-section="system">
                <h4>系统参数</h4>
                <div class="setting-item">
                    <label for="maxThreadNum">最大线程数</label>
                    <input type="number" id="maxThreadNum" min="1" max="20" value="${settings.MAX_THREAD_NUM || 5}">
                </div>
                <div class="setting-item">
                    <label for="maxNovelSummaryLength">导入小说的最大长度</label>
                    <input type="number" id="maxNovelSummaryLength" min="10000" max="1000000" value="${settings.MAX_NOVEL_SUMMARY_LENGTH || 20000}">
                </div>
            </div>
            
            <!-- 提示词配置 -->
            <div class="settings-section" data-section="prompts">
                <h4>系统提示词</h4>
                <div class="setting-item">
                    <label for="systemPrompt">默认系统提示词</label>
                    <textarea id="systemPrompt" rows="6" placeholder="输入默认的系统提示词...">${settings.SYSTEM_PROMPT || ''}</textarea>
                </div>
                <div class="setting-item">
                    <label for="creativePrompt">创作提示词模板</label>
                    <textarea id="creativePrompt" rows="4" placeholder="输入创作相关的提示词模板...">${settings.CREATIVE_PROMPT || ''}</textarea>
                </div>
            </div>
        </div>
        <div class="settings-footer">
            <button class="export-config-btn">导出配置</button>
            <button class="import-config-btn">导入配置</button>
            <button class="save-settings">保存所有设置</button>
        </div>
    `;
    
    overlay.appendChild(popup);
    document.body.appendChild(overlay);
    
    // Add event listeners
    const closeBtn = popup.querySelector('.settings-close');
    closeBtn.addEventListener('click', hideSettings);
    
    // Tab navigation
    const tabs = popup.querySelectorAll('.settings-tab');
    const sections = popup.querySelectorAll('.settings-section');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetSection = tab.dataset.tab;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active section
            sections.forEach(s => s.classList.remove('active'));
            popup.querySelector(`[data-section="${targetSection}"]`).classList.add('active');
        });
    });
    
    // Provider selector
    const providerSelect = popup.querySelector('#providerSelect');
    providerSelect.addEventListener('change', (e) => {
        if (e.target.value) {
            showProviderConfigForm(e.target.value);
        } else {
            popup.querySelector('#providerConfigForm').style.display = 'none';
        }
    });
    
    // Save settings button
    const saveBtn = popup.querySelector('.save-settings');
    saveBtn.addEventListener('click', () => {
        saveAllSettings();
        hideSettings();
    });
    
    // Export/Import config buttons
    popup.querySelector('.export-config-btn').addEventListener('click', exportConfiguration);
    popup.querySelector('.import-config-btn').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = importConfiguration;
        input.click();
    });
    
    // Reload models button
    popup.querySelector('.reload-models-btn').addEventListener('click', reloadAllModels);
    
    // Test model buttons
    const testButtons = popup.querySelectorAll('.test-model-btn');
    testButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const selectId = btn.dataset.for;
            const select = document.getElementById(selectId);
            const selectedModel = select.value;
            
            if (!selectedModel) {
                showToast('请先选择一个模型', 'error');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '测试中...';
            
            try {
                const response = await fetch(`${window._env_?.SERVER_URL}/test_model`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        provider_model: selectedModel
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('模型测试成功', 'success');
                } else {
                    showToast(`模型测试失败: ${result.error}`, 'error');
                }
            } catch (error) {
                showToast(`测试请求失败: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '测试';
            }
        });
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            hideSettings();
        }
    });
    
    // Initialize configured providers display
    updateConfiguredProvidersList();
    
    return overlay;
}

// Dynamic provider configuration functions
function showProviderConfigForm(providerId) {
    const formContainer = document.querySelector('#providerConfigForm');
    const formContent = formContainer.querySelector('.config-form-content');
    
    if (!providerId || !AI_PROVIDERS[providerId]) {
        formContainer.style.display = 'none';
        return;
    }
    
    const provider = AI_PROVIDERS[providerId];
    const savedConfig = providerConfigs[providerId] || {};
    
    // Build form HTML
    let formHTML = `<h5>配置 ${provider.name}</h5>`;
    
    provider.fields.forEach(field => {
        const value = savedConfig[field.key] || field.default || '';
        const isPassword = field.key.includes('key');
        
        formHTML += `
            <div class="config-field">
                <label for="${field.key}">${field.label}${field.required ? ' *' : ''}</label>
                <input 
                    type="${isPassword ? 'password' : 'text'}" 
                    id="${field.key}" 
                    value="${value}" 
                    placeholder="${field.default || ''}"
                    ${field.required ? 'required' : ''}
                />
            </div>
        `;
    });
    
    // Add model selection field
    if (provider.models && provider.models.length > 0) {
        formHTML += `
            <div class="config-field">
                <label for="model_name">选择模型 *</label>
                <select id="model_name" required>
                    <option value="">选择模型...</option>
                    ${provider.models.map(model => 
                        `<option value="${model}" ${savedConfig.model_name === model ? 'selected' : ''}>${model}</option>`
                    ).join('')}
                </select>
            </div>
        `;
    } else {
        // For providers with dynamic models (like LM Studio)
        formHTML += `
            <div class="config-field">
                <label for="model_name">模型名称 *</label>
                <input 
                    type="text" 
                    id="model_name" 
                    value="${savedConfig.model_name || ''}" 
                    placeholder="输入模型名称或通过'加载模型'按钮获取"
                    required
                />
            </div>
        `;
    }
    
    // Add system prompt field
    formHTML += `
        <div class="config-field">
            <label for="system_prompt">系统提示词</label>
            <textarea 
                id="system_prompt" 
                rows="3" 
                placeholder="输入默认系统提示词..."
            >${savedConfig.system_prompt || ''}</textarea>
        </div>
    `;
    
    formContent.innerHTML = formHTML;
    formContainer.style.display = 'block';
    
    // Bind action buttons
    bindProviderConfigActions(providerId);
}

function bindProviderConfigActions(providerId) {
    const formContainer = document.querySelector('#providerConfigForm');
    
    // Test connection button
    const testBtn = formContainer.querySelector('.test-connection-btn');
    testBtn.onclick = () => testProviderConnection(providerId);
    
    // Save configuration button
    const saveBtn = formContainer.querySelector('.save-provider-btn');
    saveBtn.onclick = () => saveProviderConfiguration(providerId);
    
    // Load models button
    const loadBtn = formContainer.querySelector('.load-models-btn');
    loadBtn.onclick = () => loadProviderModels(providerId);
}

async function testProviderConnection(providerId) {
    const provider = AI_PROVIDERS[providerId];
    const statusDiv = document.querySelector('.connection-status');
    const testBtn = document.querySelector('.test-connection-btn');
    
    statusDiv.innerHTML = '<div class="status-testing">🔍 正在测试连接...</div>';
    testBtn.disabled = true;
    
    try {
        const config = getProviderConfigFromForm(providerId);
        
        const response = await fetch(`${window._env_?.SERVER_URL}/api/test_provider`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                provider: providerId,
                config: config
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.innerHTML = '<div class="status-success">✅ 连接测试成功</div>';
            showToast('连接测试成功', 'success');
        } else {
            statusDiv.innerHTML = `<div class="status-error">❌ 连接失败: ${result.error}</div>`;
            showToast(`连接测试失败: ${result.error}`, 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="status-error">❌ 测试失败: ${error.message}</div>`;
        showToast(`测试失败: ${error.message}`, 'error');
    } finally {
        testBtn.disabled = false;
    }
}

async function saveProviderConfiguration(providerId) {
    const statusDiv = document.querySelector('.connection-status');
    const saveBtn = document.querySelector('.save-provider-btn');
    
    statusDiv.innerHTML = '<div class="status-saving">💾 正在保存配置...</div>';
    saveBtn.disabled = true;
    
    try {
        const config = getProviderConfigFromForm(providerId);
        
        // Validate required fields
        const provider = AI_PROVIDERS[providerId];
        for (const field of provider.fields) {
            if (field.required && !config[field.key]) {
                throw new Error(`${field.label} 不能为空`);
            }
        }
        
        // Save to localStorage
        providerConfigs[providerId] = config;
        localStorage.setItem('providerConfigs', JSON.stringify(providerConfigs));
        
        // Save to backend
        const response = await fetch(`${window._env_?.SERVER_URL}/api/save_provider_config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                provider: providerId,
                config: config
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.innerHTML = '<div class="status-success">✅ 配置保存成功</div>';
            showToast('配置保存成功', 'success');
            updateConfiguredProvidersList();
            updateModelSelects();
        } else {
            statusDiv.innerHTML = `<div class="status-error">❌ 保存失败: ${result.error}</div>`;
            showToast(`保存失败: ${result.error}`, 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="status-error">❌ 保存失败: ${error.message}</div>`;
        showToast(`保存失败: ${error.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
    }
}

async function loadProviderModels(providerId) {
    const statusDiv = document.querySelector('.connection-status');
    const loadBtn = document.querySelector('.load-models-btn');
    
    statusDiv.innerHTML = '<div class="status-loading">📋 正在加载模型列表...</div>';
    loadBtn.disabled = true;
    
    try {
        const config = getProviderConfigFromForm(providerId);
        console.log(`Loading models for provider: ${providerId}`, config);
        
        const response = await fetch(`${window._env_?.SERVER_URL}/api/load_provider_models`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                provider: providerId,
                config: config
            })
        });
        
        const result = await response.json();
        console.log(`API response for ${providerId}:`, result);
        
        if (result.success && result.models) {
            console.log(`Original models count for ${providerId}:`, AI_PROVIDERS[providerId].models.length);
            AI_PROVIDERS[providerId].models = result.models;
            console.log(`New models count for ${providerId}:`, AI_PROVIDERS[providerId].models.length);
            console.log(`First 10 models:`, result.models.slice(0, 10));
            
            statusDiv.innerHTML = `<div class="status-success">✅ 已加载 ${result.models.length} 个模型</div>`;
            showToast(`已加载 ${result.models.length} 个模型`, 'success');
            
            // Update model dropdowns if this provider is in use
            updateModelSelects();
            
            // Refresh the current provider form to show the new models
            showProviderConfigForm(providerId);
        } else {
            console.error(`Failed to load models for ${providerId}:`, result);
            statusDiv.innerHTML = `<div class="status-error">❌ 加载模型失败: ${result.error || '未知错误'}</div>`;
            showToast(`加载模型失败: ${result.error || '未知错误'}`, 'error');
        }
    } catch (error) {
        console.error(`Error loading models for ${providerId}:`, error);
        statusDiv.innerHTML = `<div class="status-error">❌ 加载失败: ${error.message}</div>`;
        showToast(`加载失败: ${error.message}`, 'error');
    } finally {
        loadBtn.disabled = false;
    }
}

function getProviderConfigFromForm(providerId) {
    const provider = AI_PROVIDERS[providerId];
    const config = {};
    
    provider.fields.forEach(field => {
        const input = document.getElementById(field.key);
        if (input) {
            config[field.key] = input.value;
        }
    });
    
    // Add model name
    const modelNameInput = document.getElementById('model_name');
    if (modelNameInput) {
        config.model_name = modelNameInput.value;
    }
    
    // Add system prompt
    const systemPromptInput = document.getElementById('system_prompt');
    if (systemPromptInput) {
        config.system_prompt = systemPromptInput.value;
    }
    
    return config;
}

function updateConfiguredProvidersList() {
    const listContainer = document.getElementById('configuredProvidersList');
    if (!listContainer) return;
    
    const configs = JSON.parse(localStorage.getItem('providerConfigs') || '{}');
    
    if (Object.keys(configs).length === 0) {
        listContainer.innerHTML = '<div class="no-providers">暂无已配置的提供商</div>';
        return;
    }
    
    let listHTML = '';
    Object.entries(configs).forEach(([providerId, config]) => {
        const provider = AI_PROVIDERS[providerId];
        if (!provider) return;
        
        const isValid = config.api_key && !config.api_key.includes('your-');
        const apiKeyDisplay = config.api_key ? 
            config.api_key.substring(0, 8) + '...' + config.api_key.slice(-4) : 
            '未设置';
        
        listHTML += `
            <div class="provider-item ${isValid ? 'valid' : 'invalid'}">
                <div class="provider-info">
                    <h6>${provider.name}</h6>
                    <p>API Key: ${apiKeyDisplay}</p>
                    <p>模型: ${config.model_name || '未选择'}</p>
                </div>
                <div class="provider-actions">
                    <button class="edit-provider-btn" onclick="editProvider('${providerId}')">编辑</button>
                    <button class="delete-provider-btn" onclick="deleteProvider('${providerId}')">删除</button>
                </div>
            </div>
        `;
    });
    
    listContainer.innerHTML = listHTML;
}

function editProvider(providerId) {
    // Set provider selector and show form
    const providerSelect = document.getElementById('providerSelect');
    providerSelect.value = providerId;
    showProviderConfigForm(providerId);
    
    // Switch to providers tab
    document.querySelector('[data-tab="providers"]').click();
}

function deleteProvider(providerId) {
    if (confirm(`确定要删除 ${AI_PROVIDERS[providerId]?.name} 的配置吗？`)) {
        delete providerConfigs[providerId];
        localStorage.setItem('providerConfigs', JSON.stringify(providerConfigs));
        updateConfiguredProvidersList();
        showToast('配置已删除', 'success');
    }
}

async function reloadAllModels() {
    const btn = document.querySelector('.reload-models-btn');
    btn.disabled = true;
    btn.textContent = '🔄 重新加载中...';
    
    try {
        const response = await fetch(`${window._env_?.SERVER_URL}/api/reload_models`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            await loadModelConfigs();
            updateModelSelects();
            showToast('模型重新加载成功', 'success');
        } else {
            showToast(`重新加载失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`重新加载失败: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 重新加载所有模型';
    }
}

async function exportConfiguration() {
    const settings = JSON.parse(localStorage.getItem('settings') || '{}');
    const providers = JSON.parse(localStorage.getItem('providerConfigs') || '{}');
    
    const config = {
        settings,
        providers,
        timestamp: new Date().toISOString(),
        version: '1.0'
    };
    
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `long-novel-gpt-config-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('配置导出成功', 'success');
}

async function importConfiguration(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        const text = await file.text();
        const config = JSON.parse(text);
        
        if (config.settings) {
            localStorage.setItem('settings', JSON.stringify(config.settings));
        }
        
        if (config.providers) {
            localStorage.setItem('providerConfigs', JSON.stringify(config.providers));
            providerConfigs = config.providers;
            updateConfiguredProvidersList();
        }
        
        showToast('配置导入成功', 'success');
        
        // Refresh the settings display
        if (document.querySelector('.settings-overlay').style.display === 'block') {
            hideSettings();
            setTimeout(() => showSettings(), 100);
        }
    } catch (error) {
        showToast(`配置导入失败: ${error.message}`, 'error');
    }
}

function saveAllSettings() {
    const settings = {
        MAIN_MODEL: document.getElementById('defaultMainModel').value,
        SUB_MODEL: document.getElementById('defaultSubModel').value,
        MAX_THREAD_NUM: parseInt(document.getElementById('maxThreadNum').value),
        MAX_NOVEL_SUMMARY_LENGTH: parseInt(document.getElementById('maxNovelSummaryLength').value),
        SYSTEM_PROMPT: document.getElementById('systemPrompt').value,
        CREATIVE_PROMPT: document.getElementById('creativePrompt').value
    };
    
    localStorage.setItem('settings', JSON.stringify(settings));
    showToast('所有设置已保存', 'success');
}

export async function loadModelConfigs() {
    try {
        // Load provider configurations from localStorage
        const savedProviderConfigs = localStorage.getItem('providerConfigs');
        if (savedProviderConfigs) {
            providerConfigs = JSON.parse(savedProviderConfigs);
        }
        
        // Load backend settings
        const response = await fetch(`${window._env_?.SERVER_URL}/setting`);
        const settings = await response.json();
        modelConfigs = settings.models;
        
        // Initialize localStorage settings if not exists
        if (!localStorage.getItem('settings')) {
            localStorage.setItem('settings', JSON.stringify({
                MAIN_MODEL: settings.MAIN_MODEL,
                SUB_MODEL: settings.SUB_MODEL,
                MAX_THREAD_NUM: settings.MAX_THREAD_NUM,
                MAX_NOVEL_SUMMARY_LENGTH: settings.MAX_NOVEL_SUMMARY_LENGTH,
                SYSTEM_PROMPT: settings.SYSTEM_PROMPT || '',
                CREATIVE_PROMPT: settings.CREATIVE_PROMPT || ''
            }));
        }
        
        // Try to load models for configured providers
        await loadConfiguredProviderModels();
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('加载设置失败', 'error');
    }
}

async function loadConfiguredProviderModels() {
    // Load models for each configured provider
    const configuredProviders = Object.keys(providerConfigs);
    
    for (const providerId of configuredProviders) {
        try {
            const config = providerConfigs[providerId];
            if (config.api_key && !config.api_key.includes('your-')) {
                // Try to load models from backend if available
                const response = await fetch(`${window._env_?.SERVER_URL}/api/get_provider_models`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        provider: providerId,
                        config: config
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success && result.models) {
                        AI_PROVIDERS[providerId].models = result.models;
                    }
                }
            }
        } catch (error) {
            console.warn(`Failed to load models for provider ${providerId}:`, error);
        }
    }
}

function updateModelSelects() {
    const mainModelSelect = document.getElementById('defaultMainModel');
    const subModelSelect = document.getElementById('defaultSubModel');
    
    if (!mainModelSelect || !subModelSelect) return;
    
    mainModelSelect.innerHTML = '';
    subModelSelect.innerHTML = '';
    
    // Get configured providers from localStorage
    const configuredProviders = JSON.parse(localStorage.getItem('providerConfigs') || '{}');
    
    // Only add models from configured providers
    Object.entries(configuredProviders).forEach(([providerId, config]) => {
        const provider = AI_PROVIDERS[providerId];
        if (!provider) return;
        
        // Check if provider is properly configured
        if (config.api_key && !config.api_key.includes('your-') && config.model_name) {
            // Add the configured model for this provider
            const option = document.createElement('option');
            option.value = `${providerId}/${config.model_name}`;
            option.textContent = `${provider.name}/${config.model_name}`;
            
            mainModelSelect.appendChild(option.cloneNode(true));
            subModelSelect.appendChild(option.cloneNode(true));
        }
        
        // Also add other available models from this provider if they exist
        if (provider.models && provider.models.length > 0) {
            provider.models.forEach(model => {
                // Skip if this is already the configured model
                if (model === config.model_name) return;
                
                const option = document.createElement('option');
                option.value = `${providerId}/${model}`;
                option.textContent = `${provider.name}/${model}`;
                
                // Check if this combination already exists to avoid duplicates
                const existingMain = Array.from(mainModelSelect.options).find(opt => opt.value === option.value);
                const existingSub = Array.from(subModelSelect.options).find(opt => opt.value === option.value);
                
                if (!existingMain) {
                    mainModelSelect.appendChild(option.cloneNode(true));
                }
                if (!existingSub) {
                    subModelSelect.appendChild(option.cloneNode(true));
                }
            });
        }
    });
    
    // If no models available, add placeholder
    if (mainModelSelect.options.length === 0) {
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = '请先配置AI提供商';
        placeholder.disabled = true;
        
        mainModelSelect.appendChild(placeholder.cloneNode(true));
        subModelSelect.appendChild(placeholder.cloneNode(true));
    }
}

function loadCurrentSettings() {
    const settings = JSON.parse(localStorage.getItem('settings'));
    const mainModelSelect = document.getElementById('defaultMainModel');
    const subModelSelect = document.getElementById('defaultSubModel');
    
    if (mainModelSelect.options.length > 0) {
        mainModelSelect.value = settings.MAIN_MODEL;
    }
    if (subModelSelect.options.length > 0) {
        subModelSelect.value = settings.SUB_MODEL;
    }

    // Load max thread number and novel summary length
    document.getElementById('maxThreadNum').value = settings.MAX_THREAD_NUM;
    document.getElementById('maxNovelSummaryLength').value = settings.MAX_NOVEL_SUMMARY_LENGTH;
}

function saveSettings() {
    const settings = {
        MAIN_MODEL: document.getElementById('defaultMainModel').value,
        SUB_MODEL: document.getElementById('defaultSubModel').value,
        MAX_THREAD_NUM: parseInt(document.getElementById('maxThreadNum').value),
        MAX_NOVEL_SUMMARY_LENGTH: parseInt(document.getElementById('maxNovelSummaryLength').value)
    };
    
    localStorage.setItem('settings', JSON.stringify(settings));
    showToast('设置已保存', 'success');
}

export function showSettings(_previousMode) {
    // Store current mode before switching to settings
    previousMode = _previousMode;
    
    let overlay = document.querySelector('.settings-overlay');
    if (!overlay) {
        overlay = createSettingsPopup();
        updateModelSelects();
    }

    loadCurrentSettings();
    overlay.style.display = 'block';
}

function hideSettings() {
    const overlay = document.querySelector('.settings-overlay');
    if (overlay) {
        overlay.style.display = 'none';
        
        // Switch back to previous mode
        if (previousMode) {
            const previousTab = document.querySelector(`.mode-tab[data-value="${previousMode}"]`);
            if (previousTab) {
                previousTab.click();
            }
        }
    }
}