# Public deploy config for robonix.service.piper_with_linkerhand.object_detect.
# Values below are the ones this deploy uses; the type/unit/constraint note
# above each key is the contract.
config:
  # ── backend selection ───────────────────────────────────────────────────
  # string, default: llm; accepted values: llm, yolo_http.
  # `llm` (upstream's only backend) sends the frame to an OpenAI-compatible
  # multimodal model. `yolo_http` POSTs a JPEG to an external detector and
  # returns its boxes verbatim — added here so the heavy model can run on the
  # host GPU instead of inside the ROS container, which deliberately carries no
  # torch. The response's bbox_2d carries a 5TH element (OBB rotation in
  # degrees) and is forwarded unchanged.
  detect_backend: yolo_http

  # string, required for yolo_http. Full URL of the detector's /detect endpoint.
  yolo_http_url: "http://127.0.0.1:8770/detect"

  # float, seconds, default: 10.0; must be > 0.
  yolo_http_timeout_s: 10.0

  # float, default: None (omitted from the request). Confidence / NMS IoU
  # thresholds forwarded to the detector; the host service has its own
  # defaults, so leaving these unset is the normal case.
  yolo_conf: 0.5
  yolo_iou: 0.45

  # ── VLM backend (configured at deploy level, not here) ──────────────────
  # In this deploy the VLM route is deliberately left unusable: the pilot's
  # model is a TEXT model, so pointing the detector at it would fail at request
  # time and the service treats "no llm_base_url/llm_model" as "route
  # unavailable" rather than an error. Every class this robot knows
  # (carrot / potato / tomato) is served by the yolo_http backend.
  #
  # string (OpenAI-compatible endpoint); default "".
  # llm_base_url: https://api.example.com/v1
  # string; default "".
  # llm_model: some-multimodal-model
  # string, default: "any". Sent as the bearer token.
  # llm_api_key: "any"
  # float, seconds, default: 30.0; integer, default: 1; float, default: 0.0.
  llm_timeout_s: 30.0
  llm_max_retries: 1
  temperature: 0.0
  # string, optional. Path to the prompt file overriding the built-in prompts.
  # prompts_file: ""

  # ── frame sources ───────────────────────────────────────────────────────
  # string, default: "". Empty => resolve the camera's RGB endpoint through
  # atlas, falling back to /camera/color/image_raw. The fallback names are
  # exactly what the Orbbec driver publishes.
  rgb_topic: ""
  # string, default: "". Only used when skip_depth is false.
  depth_topic: ""
  # string, default: "". Empty => /camera/color/camera_info.
  camera_info_topic: ""
  # string, optional. Pin the camera provider instead of letting atlas choose.
  # camera_provider_id: orbbec_camera

  # boolean, default: false. Skip the depth stream entirely — this pipeline
  # maps the bbox through a 2D homography, so depth is never read.
  skip_depth: true

  # boolean, default: false. Set true when the camera is mounted opposite to
  # the arm (mirrors the projected x). Applies to the VLM backend only.
  rotation_cam2arm: false
