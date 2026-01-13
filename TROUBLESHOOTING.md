# Earnetics Command Center Troubleshooting

Common issues and solutions for the 3D Command Center on Windows 11.

## 1. Connection Issues

### Backend Unreachable
- **Symptom**: "Backend unreachable" in Stripe panel or console errors.
- **Fix**: Ensure the backend is running on `http://127.0.0.1:8001`. Check if another process is using the port.
- **Command**: `netstat -ano | findstr :8001`

### WebSocket Disconnected
- **Symptom**: Real-time updates not reflecting in the 3D scene.
- **Fix**: Verify `VITE_WS_URL` in `packages/renderer/.env` matches the backend WebSocket URL (`ws://127.0.0.1:8001/ws`).

## 2. Build Failures

### TypeScript Errors
- **Symptom**: `npm run build` fails with type errors.
- **Fix**: Ensure all `@types` are installed. Run `npm install` in the root.
- **Note**: Some Three.js version mismatches are bypassed with `any` casts in `OpsRoom.tsx` for stability.

### Missing .env
- **Symptom**: API calls failing or pointing to wrong URLs.
- **Fix**: Ensure `packages/renderer/.env` exists and contains `VITE_API_URL` and `VITE_WS_URL`.

## 3. Stripe Integration

### Stripe Offline
- **Symptom**: Stripe panel shows **OFFLINE**.
- **Fix**: Check `STRIPE_SECRET_KEY` in your environment. Verify the backend logs for initialization errors.
- **Log Check**: Look for `StripePaymentProcessor initialized` in the backend console.

## 4. Windows 11 Specifics

### Execution Policy
- **Symptom**: Cannot run `.ps1` scripts or `npm` commands.
- **Fix**: Set execution policy to `RemoteSigned`.
- **Command**: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
