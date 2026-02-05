import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import type { Agent } from '../../../stores/agentStore';
import { useAgentStore } from '../../../stores/agentStore';

// Default camera position - closer overhead so deck is visible
const DEFAULT_CAMERA_POSITION = new THREE.Vector3(0, 18, 26);
const DEFAULT_CAMERA_TARGET = new THREE.Vector3(0, 0, 0);
const DEFAULT_FOV = 45;

export interface CameraRigRef {
  resetView: () => void;
  focusOnPosition: (position: [number, number, number], target?: [number, number, number]) => void;
}

interface CameraRigProps {
  targetAgent?: Agent | null;
  enableFocus?: boolean;
}

export const CameraRig = forwardRef<CameraRigRef, CameraRigProps>(
  ({ targetAgent, enableFocus = true }, ref) => {
    const { camera } = useThree();
    const controlsRef = useRef<any>(null);
    const isAnimatingRef = useRef(false);
    const rafIdRef = useRef<number | null>(null);
    const { selectedDepartment } = useAgentStore();

    // Set initial camera position/target on mount
    useEffect(() => {
      if (!camera) return;
      camera.position.copy(DEFAULT_CAMERA_POSITION);
      camera.fov = DEFAULT_FOV;
      camera.updateProjectionMatrix();
      if (controlsRef.current) {
        controlsRef.current.target.copy(DEFAULT_CAMERA_TARGET);
        controlsRef.current.update();
      }
    }, [camera]);

    // Cleanup RAF on unmount
    useEffect(() => {
      return () => {
        if (rafIdRef.current !== null) {
          cancelAnimationFrame(rafIdRef.current);
          rafIdRef.current = null;
        }
        isAnimatingRef.current = false;
      };
    }, []);

    // Reset camera to default view
    const resetView = () => {
      if (!controlsRef.current || !camera) return;
      
      // Cancel any existing animation
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
      
      isAnimatingRef.current = true;
      
      // Smoothly animate to default position
      const startPos = camera.position.clone();
      const startTarget = controlsRef.current.target.clone();
      
      let progress = 0;
      const duration = 1000; // 1 second
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        // Ease in-out
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        // Lerp camera position
        camera.position.lerpVectors(startPos, DEFAULT_CAMERA_POSITION, eased);
        
        // Lerp target
        controlsRef.current.target.lerpVectors(startTarget, DEFAULT_CAMERA_TARGET, eased);
        controlsRef.current.update();
        
        if (progress < 1) {
          rafIdRef.current = requestAnimationFrame(animate);
        } else {
          isAnimatingRef.current = false;
          rafIdRef.current = null;
        }
      };
      
      rafIdRef.current = requestAnimationFrame(animate);
    };

    // Focus on a specific position - preserves current orbit direction
    const focusOnPosition = (
      position: [number, number, number],
      target?: [number, number, number]
    ) => {
      if (!controlsRef.current || !camera) return;
      
      // Cancel any existing animation
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
      
      isAnimatingRef.current = true;
      
      const lookAtPos = target ? new THREE.Vector3(...target) : new THREE.Vector3(...position);
      
      // Get current orbit direction relative to current target
      const currentTarget = controlsRef.current.target.clone();
      const viewDir = camera.position.clone().sub(currentTarget).normalize();
      
      // Calculate final camera position preserving orbit direction
      const distance = 15; // Distance from target
      const height = 8; // Height offset
      
      const finalCameraPos = new THREE.Vector3()
        .copy(lookAtPos)
        .add(viewDir.clone().multiplyScalar(distance))
        .add(new THREE.Vector3(0, height, 0));
      
      const startPos = camera.position.clone();
      const startTarget = currentTarget.clone();
      
      let progress = 0;
      const duration = 1500; // 1.5 seconds
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        // Ease in-out
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        // Lerp camera position
        camera.position.lerpVectors(startPos, finalCameraPos, eased);
        
        // Lerp target
        controlsRef.current.target.lerpVectors(startTarget, lookAtPos, eased);
        controlsRef.current.update();
        
        if (progress < 1) {
          rafIdRef.current = requestAnimationFrame(animate);
        } else {
          isAnimatingRef.current = false;
          rafIdRef.current = null;
        }
      };
      
      rafIdRef.current = requestAnimationFrame(animate);
    };

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      resetView,
      focusOnPosition,
    }));

    // Smooth focus on selected agent/department
    useEffect(() => {
      if (!enableFocus) return;
      
      // Cancel previous animation if starting new one
      if (isAnimatingRef.current && rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
        isAnimatingRef.current = false;
      }
      
      if (targetAgent) {
        // Focus on selected agent
        const agentPos: [number, number, number] = [
          targetAgent.position[0],
          targetAgent.position[1] + 2,
          targetAgent.position[2],
        ];
        focusOnPosition(agentPos, agentPos);
      } else if (selectedDepartment) {
        // Focus on selected department (find zone position)
        const departmentZones = [
          { department: 'Executive Board', position: [0, 2, 0] as [number, number, number] },
          { department: 'Finance & Revenue', position: [18, 0, 0] as [number, number, number] },
          { department: 'Creative & Product', position: [-18, 0, 0] as [number, number, number] },
          { department: 'Tech & Infrastructure', position: [0, 0, 18] as [number, number, number] },
          { department: 'Legal & Sovereignty', position: [0, 0, -18] as [number, number, number] },
          { department: 'Health & Human Factor', position: [12.7, 0, 12.7] as [number, number, number] },
          { department: 'Corporate Analytics', position: [-12.7, 0, 12.7] as [number, number, number] },
          { department: 'Corporate Execution', position: [12.7, 0, -12.7] as [number, number, number] },
          { department: 'Email Marketing', position: [-12.7, 0, -12.7] as [number, number, number] },
          { department: 'Revenue Strategy Cell', position: [-18.5, 0, 7.7] as [number, number, number] },
          { department: 'Revenue Execution', position: [18.5, 0, -7.7] as [number, number, number] },
          { department: 'Lead Generation & Acquisition', position: [-7.7, 0, 18.5] as [number, number, number] },
          { department: 'Website Growth & Digital Presence', position: [7.7, 0, -18.5] as [number, number, number] },
        ];
        
        const zone = departmentZones.find(z => z.department === selectedDepartment);
        if (zone) {
          focusOnPosition(zone.position, zone.position);
        }
      }
    }, [targetAgent, selectedDepartment, enableFocus]);

    // Smooth camera updates
    useFrame(() => {
      if (controlsRef.current) {
        controlsRef.current.update();
      }
    });

    return (
      <OrbitControls
        ref={controlsRef}
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={6}
        maxDistance={80}
        minPolarAngle={0.1} // Prevent going below ground
        maxPolarAngle={Math.PI / 2.1} // Prevent flipping upside down
        enableDamping={true}
        dampingFactor={0.05}
        target={DEFAULT_CAMERA_TARGET}
      />
    );
  }
);

CameraRig.displayName = 'CameraRig';
