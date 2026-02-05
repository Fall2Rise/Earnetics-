import { create } from 'zustand';

interface DebugState {
    showFog: boolean;
    showEnvironment: boolean;
    showKeyLight: boolean;
    showFillLight: boolean;
    showRimLight: boolean;
    showPointLights: boolean;
    showSpotLight: boolean;
    showAmbientLight: boolean;
    showBloom: boolean;
    showChromaticAberration: boolean;
    showNoise: boolean;
    showVignette: boolean;

    toggle: (key: keyof Omit<DebugState, 'toggle'>) => void;
}

export const useDebugStore = create<DebugState>((set) => ({
    showFog: true,
    showEnvironment: true,
    showKeyLight: true,
    showFillLight: true,
    showRimLight: true,
    showPointLights: true,
    showSpotLight: true,
    showAmbientLight: true,
    showBloom: true,
    showChromaticAberration: true,
    showNoise: true,
    showVignette: true,

    toggle: (key) => set((state) => ({ [key]: !state[key] })),
}));
