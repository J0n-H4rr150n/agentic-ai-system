            }
        ]
    },

human_approval: {
    fields: [
        {
            key: 'title',
            label: 'Approval Title',
            type: 'text',
            placeholder: 'Review Proposed Action',
            default: 'Human Approval Required',
            required: true,
            help: 'Title shown in approval prompt'
        },
        {
            key: 'message',
            label: 'Message',
            type: 'textarea',
            placeholder: 'The agent wants to perform the following action...',
            rows: 3,
            required: true,
            help: 'Explanation of what needs approval'
        },
        {
            key: 'show_state_keys',
            label: 'State Keys to Display (JSON Array)',
            type: 'textarea',
            placeholder: '["llm_action", "llm_confidence", "llm_reasoning"]',
            rows: 2,
            help: 'Which state values to show for context (JSON array of strings)'
        },
        {
            key: 'timeout_seconds',
            label: 'Timeout (seconds)',
            type: 'number',
            default: 300,
            min: 10,
            max: 3600,
            help: 'Auto-reject after this many seconds'
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
