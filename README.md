# service-piper_with_linkerhand-object-detect-rbnx

Robonix package for **object detection**. It exposes an atlas-routed MCP service and replaces the older `yolo_world_rbnx` path. Owns the `service/perception/object_detect/*` namespace.

Catalog name: `robonix.service.piper_with_linkerhand.object_detect`.

> **Provenance — vendored repackaging.** Copied from
> `syswonder/service-object-detect-rbnx` @ `64cbb3c` (main, 2026-09-15) so the
> roboarm deploy owns everything but the camera package. License unchanged
> (MulanPSL-2.0). **Local difference:** a `detect_backend: yolo_http` backend
> that POSTs a JPEG to an external YOLO/OBB server (the roboarm deploy runs the
> host-GPU detector that way). Upstream is VLM-only by design — "no GPU /
> ultralytics weights". Everything below describes the shared, upstream
> behaviour unless it says `yolo_http`.

## Capability surface

| Contract                                                  | Mode | Transport | Source / handler                                          |
| --------------------------------------------------------- | ---- | --------- | --------------------------------------------------------- |
| `robonix/service/perception/object_detect/driver`         | rpc  | gRPC      | `Driver(CMD_INIT, config_json)` — lifecycle gate          |
| `robonix/service/perception/object_detect/detect_object`  | rpc  | MCP       | `DetectObject(object_name) → bbox_2d + object_center_3d`  |

There is no legacy `/yolo/detect_object` ROS-service fallback in this package.

## Compared with the old `yolo_world` path

- no GPU / ultralytics weights;
- RGB → OpenAI-compatible VLM → 2D bbox;
- in vertical-grasp mode the depth stream is completely unused (`skip_depth=true`); `service-piper_with_linkerhand-grasp-pose-rbnx` maps the bbox center through the calibrated 2D homography and combines it with the configured tabletop z.

## Boot ordering

Must come **after** `primitive-orbbec-dabai_dcw-camera-rbnx` in the deploy manifest — Init resolves the RGB topic (and, when `skip_depth=false`, the depth topic) at atlas-registration time.

## Driver-init lifecycle

`start.sh` brings up the atlas bridge — no ROS spawn. The bridge opens a gRPC server, registers the capability and declares only `object_detect/driver`, then blocks awaiting `Driver(CMD_INIT, config_json)`.

When `rbnx boot` invokes Init the handler:

1. validates the LLM endpoint / API key / model name;
2. resolves `primitive/camera/rgb` and `primitive/camera/camera_info` via atlas (depth is skipped when `skip_depth=true`);
3. declares `object_detect/detect_object` on atlas.

## Layout

```
service-piper_with_linkerhand-object-detect-rbnx/
├── package_manifest.yaml
├── capabilities/
│   └── service/perception/object_detect/{driver,detect_object}.v1.toml
├── config/                     example .env / prompt templates
├── llm_detect/                 Python package: atlas bridge + VLM client
├── scripts/
│   ├── build.sh                colcon build + rbnx codegen
│   └── start.sh                source ROS, exec atlas_bridge
└── src/                        vendored dependencies (if any)
```

## Config (passed via `Driver(CMD_INIT, config_json)`)

```json
{
  "llm_base_url":       "https://api.ofox.ai/v1",
  "llm_api_key":        "sk-...",
  "llm_model":          "google/gemini-3.1-flash-lite",
  "temperature":        0.0,
  "rotation_cam2arm":   true,
  "skip_depth":         true,
  "rgb_topic":          "",
  "camera_info_topic":  ""
}
```

- `rotation_cam2arm`: rotate the image 180° before sending to the LLM when the camera is mounted opposite to the arm.
- `skip_depth`: vertical-grasp mode — bypass depth back-projection entirely. `env LLM_DETECT_SKIP_DEPTH=1` is the fallback.
- Empty topic strings mean "atlas-resolved"; defaults already match `primitive-orbbec-dabai_dcw-camera-rbnx`.

## Build / run standalone

```bash
bash scripts/build.sh                           # colcon + rbnx codegen
ROBONIX_ATLAS=127.0.0.1:50051 \
    bash scripts/start.sh                       # registers, awaits Init
```

## Verification

```bash
rbnx caps | grep object_detect
# Expected: llm_detect provider with
#   robonix/service/perception/object_detect/{driver, detect_object}

# End-to-end via the atlas MCP surface:
rbnx ask "where is the paper on the desk?"

# The package intentionally has no direct ROS service surface.
```

## License

This package: MulanPSL-2.0.
