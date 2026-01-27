# Running Custom Models on Raspberry Pi AI HAT+ 2 (Hailo-10H)

To run a custom model on the Hailo-10H (the chip in the GenAI Kit/AI HAT+ 2), you must use the **Hailo Dataflow Compiler (DFC)**. This compiler runs on a powerful host machine (x86 Linux/Windows), *not* on the Raspberry Pi itself.

## The Workflow: Train $\to$ ONNX $\to$ HEF $\to$ Run

### 1. Train & Export to ONNX (On your Training Machine)
Train your model in PyTorch or TensorFlow as usual. When finished, export it to ONNX.
*   **Critical Constraint:** Your model architecture must be supported by the Hailo compiler. Most standard architectures (ResNet, YOLO, MobileNet, ViT) work fine. Custom layers may require extra work.

**PyTorch Example:**
```python
import torch
import torchvision

# 1. Load/Train your model
model = torchvision.models.resnet18(pretrained=True)
model.eval()

# 2. Create dummy input matching your input shape (Batch, Channel, Height, Width)
dummy_input = torch.randn(1, 3, 224, 224)

# 3. Export to ONNX
torch.onnx.export(model, dummy_input, "my_custom_model.onnx",
                  opset_version=12,
                  input_names=['input'],
                  output_names=['output'])
```

### 2. Compile with Hailo DFC (On x86 Host Machine)
You need to install the **Hailo Dataflow Compiler** (available from the [Hailo Developer Zone](https://hailo.ai/developer-zone/)) on a standard PC/Laptop (Ubuntu recommended). This process requires a **calibration dataset** (a small set of unlabelled images from your training data) to quantize the model from Float32 to Int8 without losing accuracy.

**Compilation Script (`compile_hef.py`):**
```python
from hailo_sdk_client import ClientRunner

model_name = "my_custom_model"
onnx_path = "my_custom_model.onnx"

# 1. Parse the ONNX file
runner = ClientRunner(hw_arch="hailo10h") # Specify hailo10h for your kit
runner.translate_onnx_model(onnx_path, model_name)

# 2. Optimize (optional but recommended)
# runner.optimize(calib_dataset) 

# 3. Quantize (Requires Calibration Data)
# Load your calibration images as a list of numpy arrays
# calib_data = [np.array(img) for img in images] 
runner.optimize_full_precision() # OR use runner.quantize(calib_data) for Int8

# 4. Compile to HEF
hef = runner.compile()

# 5. Save the file
with open(f"{model_name}.hef", "wb") as f:
    f.write(hef)
```
*Note: For the best performance, you should use `runner.quantize()` with real data instead of `optimize_full_precision()`.*

### 3. Run on Raspberry Pi (Inference)
Transfer the `.hef` file to your Raspberry Pi. You can now use the HailoRT (Runtime) to run it.

```python
from hailo_platform import HEF, VDevice, HailoStreamInterface, InferVStreams, ConfigureParams, InputVStreamParams, OutputVStreamParams

# 1. Initialize Device
params = VDevice.create_params()
with VDevice(params) as target:
    
    # 2. Load HEF
    hef = HEF("my_custom_model.hef")
    
    # 3. Configure
    configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
    network_group = target.configure(hef, configure_params)[0]
    network_group_params = network_group.create_params()
    
    # 4. Create Input/Output Streams
    input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)
    output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)

    # 5. Inference Loop
    with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as infer_pipeline:
        input_data = {input_vstreams_params[0].name: my_processed_image}
        output = infer_pipeline.infer(input_data)
        print(output)
```

### Important Notes for Hailo-10H
1.  **GenAI vs. Vision:** The process above is standard for **Vision** models (Detection, Segmentation). If you are trying to run a **Large Language Model (LLM)**, the flow is different and relies on the `hailo_model_zoo_genai` scripts which handle the complex quantization and splitting of the model required for transformers.
2.  **Software Version:** Ensure your DFC version supports `hailo10h`. You usually need the latest version available in the Developer Zone.
