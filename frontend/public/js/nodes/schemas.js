// Node configuration schemas
// Defines the form fields for each node type based on ACTUAL usage

export const NODE_SCHEMAS = {
    start: {
        fields: [
            {
                key: 'initial_state.target_url',
                label: 'Target URL',
                type: 'url',
                placeholder: 'http://localhost:10303/',
                help: 'Initial URL to start the workflow'
            }
        ]
    },

    browser: {
        fields: [
            {
                key: 'action',
                label: 'Action',
                type: 'select',
                options: ['navigate', 'click', 'type', 'screenshot'],
                default: 'navigate',
                required: true,
                help: 'Browser action to perform'
            },
            {
                key: 'url_key',
                label: 'URL Key',
                type: 'text',
                placeholder: 'target_url',
                default: 'target_url',
                help: 'State key containing the URL to navigate to'
            },
            {
                key: 'observation_mode',
                label: 'Observation Mode',
                type: 'select',
                options: ['visual', 'text', 'dom', 'hybrid'],
                default: 'visual',
                help: 'How to capture page content'
            },
            {
                key: 'output_key',
                label: 'Output Key',
                type: 'text',
                placeholder: 'browser_output',
                default: 'browser_output',
                help: 'State key to store browser output'
            }
        ]
    },

    llm: {
        fields: [
            {
                key: 'model',
                label: 'Model',
                type: 'select',
                options: [
                    'gemini-1.5-flash',
                    'gemini-2.5-pro',
                    'gemini-2.5-flash',
                    'qwen-3-coder',
                    'qwen-3-security'
                ],
                default: 'gemini-1.5-flash',
                required: true
            },
            {
                key: 'prompt',
                label: 'Prompt',
                type: 'textarea',
                placeholder: 'Enter your prompt template...',
                rows: 4,
                required: true,
                help: 'LLM prompt template'
            },
            {
                key: 'json_mode',
                label: 'JSON Mode',
                type: 'checkbox',
                default: false,
                help: 'Force output to be valid JSON'
            },
            {
                key: 'output_key',
                label: 'Output Key',
                type: 'text',
                placeholder: 'llm_output',
                default: 'llm_output',
                help: 'State key to store LLM response'
            }
        ]
    },

    router: {
        fields: [
            {
                key: 'output_key',
                label: 'Output Key',
                type: 'text',
                placeholder: 'router_output',
                default: 'router_output',
                help: 'State key to store routing decision'
            },
            {
                key: 'default_output',
                label: 'Default Output',
                type: 'text',
                placeholder: 'default',
                default: 'default',
                help: 'Default output port if no conditions match'
            },
            {
                key: 'conditions',
                label: 'Conditions (JSON Array)',
                type: 'textarea',
                placeholder: '[{"var": "state.value", "op": "contains", "value": "text", "output": "found"}]',
                rows: 6,
                help: 'Array of condition objects to evaluate (must be valid JSON)'
            }
        ]
    },

    end: {
        fields: [
            {
                key: 'result_key',
                label: 'Result Key',
                type: 'text',
                placeholder: 'result',
                default: 'result',
                help: 'State key to extract as final workflow result'
            }
        ]
    },

    agent: {
        fields: [
            {
                key: 'workflow_id',
                label: 'Workflow ID',
                type: 'text',
                placeholder: 'workflow-uuid',
                required: true,
                help: 'ID of the nested workflow to execute'
            },
            {
                key: 'input_mapping',
                label: 'Input Mapping (JSON)',
                type: 'textarea',
                placeholder: '{"prompt": "state.user_input"}',
                rows: 3,
                help: 'Map current state to nested workflow inputs (JSON)'
            }
        ]
    },

    loop: {
        fields: [
            {
                key: 'workflow_id',
                label: 'Workflow ID',
                type: 'text',
                placeholder: 'workflow-uuid',
                required: true,
                help: 'ID of the workflow to loop'
            },
            {
                key: 'max_iterations',
                label: 'Max Iterations',
                type: 'number',
                min: 1,
                max: 100,
                default: 10,
                required: true,
                help: 'Maximum number of loop iterations'
            },
            {
                key: 'break_condition',
                label: 'Break Condition',
                type: 'textarea',
                placeholder: 'state.done === true',
                rows: 2,
                help: 'Expression to stop looping early'
            }
        ]
    },

    http_request: {
        fields: [
            {
                key: 'url',
                label: 'URL',
                type: 'url',
                placeholder: 'https://api.example.com/endpoint',
                required: true
            },
            {
                key: 'method',
                label: 'HTTP Method',
                type: 'select',
                options: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                default: 'GET',
                required: true
            },
            {
                key: 'headers',
                label: 'Headers (JSON)',
                type: 'textarea',
                placeholder: '{"Authorization": "Bearer token"}',
                rows: 3,
                help: 'HTTP headers as JSON object'
            },
            {
                key: 'body',
                label: 'Request Body',
                type: 'textarea',
                placeholder: '{"key": "value"}',
                rows: 4,
                help: 'Request body (JSON or text)'
            }
        ]
    },

    container: {
        fields: [
            {
                key: 'description',
                label: 'Description',
                type: 'textarea',
                placeholder: 'Describe what this container groups...',
                rows: 2,
                help: 'Optional description of this container\'s purpose'
            }
        ]
    }
};

// Get schema for a node type, or null if not defined
export function getSchemaForType(type) {
    return NODE_SCHEMAS[type] || null;
}

// Get default config for a node type
export function getDefaultConfig(type) {
    const schema = getSchemaForType(type);
    if (!schema) return {};

    const config = {};
    for (const field of schema.fields) {
        if (field.default !== undefined) {
            // Handle nested keys like 'initial_state.target_url'
            if (field.key.includes('.')) {
                const parts = field.key.split('.');
                let current = config;
                for (let i = 0; i < parts.length - 1; i++) {
                    if (!current[parts[i]]) {
                        current[parts[i]] = {};
                    }
                    current = current[parts[i]];
                }
                current[parts[parts.length - 1]] = field.default;
            } else {
                config[field.key] = field.default;
            }
        }
    }
    return config;
}
