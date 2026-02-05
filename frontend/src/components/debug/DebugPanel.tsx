import React from 'react';
import { useDebugStore } from '../../stores/debugStore';

export const DebugPanel: React.FC = () => {
    const store = useDebugStore();
    const keys = Object.keys(store).filter((k) => k.startsWith('show')) as Array<keyof typeof store>;

    return (
        <div style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: 'rgba(0, 0, 0, 0.8)',
            padding: '15px',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
            zIndex: 9999,
            border: '1px solid #333',
            maxHeight: '80vh',
            overflowY: 'auto'
        }}>
            <h3 style={{ marginTop: 0, marginBottom: '10px', borderBottom: '1px solid #555', paddingBottom: '5px' }}>
                Visual Debugger
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                {keys.map((key) => (
                    <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        <input
                            type="checkbox"
                            checked={store[key] as boolean}
                            onChange={() => store.toggle(key as any)}
                        />
                        {key.replace('show', '')}
                    </label>
                ))}
            </div>
        </div>
    );
};
