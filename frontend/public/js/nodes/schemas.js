// Node configuration schemas
// Defines the form fields for each node type

export const NODE_SCHEMAS = {
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
                required: true
            },
            {
                key: 'temperature',
                label: 'Temperature',
                type: 'number',
                min: 0,
                max: 1,
                step: 0.1,
                default: 0.7,
                help: 'Controls randomness (0 = deterministic, 1 = creative)'
            },
            {
                key: 'max_tokens',
                label: 'Max Tokens',
                type: 'number',
                min: 1,
                max: 8192,
                step: 1,
                default: 2048,
                help: 'Maximum length of generated response'
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
                help: 'Key name for storing the result in state'
            }
        ]
    },

    browser: {
        fields: [
            {
                key: 'url',
                label: 'URL',
                type: 'url',
                placeholder: 'https://example.com',
                required: true,
                help: 'Target URL to navigate to'
            },
            {
                key: 'wait_for',
                label: 'Wait For Selector',
                type: 'text',
                placeholder: 'CSS selector (optional)',
                help: 'Wait for this element to appear before continuing'
            },
            {
                key: 'screenshot',
                label: 'Take Screenshot',
                type: 'checkbox',
                default: true,
                help: 'Capture screenshot of the page'
            },
            {
                key: 'extract_text',
                label: 'Extract Text',
                type: 'checkbox',
                default: true,
                help: 'Extract visible text from the page'
            },
            {
                key: 'capture_network',
                label: 'Capture Network Logs',
                type: 'checkbox',
                default: false,
                help: 'Record network requests/responses'
            }
        ]
    },

    router: {
        fields: [
            {
                key: 'condition',
                label: 'Condition',
                type: 'textarea',
                placeholder: 'state.some_value > 10',
                rows: 2,
                required: true,
                help: 'Expression to evaluate for routing decision'
            },
            {
                key: 'true_port',
                label: 'True Output Port',
                type: 'text',
                default: 'true',
                help: 'Port name when condition is true'
            },
            {
                key: 'false_port',
                label: 'False Output Port',
                type: 'text',
                default: 'false',
                help: 'Port name when condition is false'
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
                label: 'Input Mapping',
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
                label: 'Headers',
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
    },

    // Start and End nodes have minimal/no config
    start: {
        fields: []
    },

    end: {
        fields: [
            {
                key: 'output_key',
                label: 'Output Key',
                type: 'text',
                placeholder: 'result',
                help: 'Key to extract from state as final output'
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
            config[field.key] = field.default;
        }
    }
    return config;
}
