import time

import psutil
from memory_profiler import profile
from unstructured.partition.pdf import partition_pdf

# os.makedirs("text/", exist_ok=True)


@profile
def profile_partitioning(model_name, output_filename):
    local_pdf_path = "test_pdfs/syed_haris_ali_2023_SEPTEMBER (3).pdf"

    start_time = time.time()

    # Memory profiler will print memory usage for each line
    yolox_elements = partition_pdf(
        filename=local_pdf_path,
        include_page_breaks=True,
        strategy="hi_res",
        hi_res_model_name=model_name,
    )
    print(yolox_elements)

    elapsed_time = time.time() - start_time

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n\n".join([str(e) for e in yolox_elements]))

    return elapsed_time


def profile_cpu_memory(model_name, output_filename):
    process = psutil.Process()
    start_cpu_percent = process.cpu_percent()
    start_memory_usage = process.memory_info().rss

    elapsed_time = profile_partitioning(model_name, output_filename)

    end_cpu_percent = process.cpu_percent()
    end_memory_usage = process.memory_info().rss

    return (
        elapsed_time,
        start_cpu_percent,
        end_cpu_percent,
        start_memory_usage,
        end_memory_usage,
    )


if __name__ == "__main__":
    # Profile yolox model
    (
        elapsed_time_yolox,
        start_cpu_yolox,
        end_cpu_yolox,
        start_memory_yolox,
        end_memory_yolox,
    ) = profile_cpu_memory("yolox", "zoutput-yolox.txt")
    print(f"Time taken for yolox: {elapsed_time_yolox} seconds")
    print(f"CPU usage for yolox: {end_cpu_yolox - start_cpu_yolox}%")
    print(f"Memory usage for yolox: {end_memory_yolox - start_memory_yolox} bytes")

    # # Profile quantized yolox model
    # (
    #     elapsed_time_quantized,
    #     start_cpu_quantized,
    #     end_cpu_quantized,
    #     start_memory_quantized,
    #     end_memory_quantized,
    # ) = profile_cpu_memory("yolox_quantized", "zoutput-yolox-quantized.txt")
    # print(f"Time taken for quantized yolox: {elapsed_time_quantized} seconds")
    # print(f"CPU usage for quantized yolox: {end_cpu_quantized - start_cpu_quantized}%")
    # print(
    #     f"Memory usage for quantized yolox: {end_memory_quantized - start_memory_quantized} bytes"
    # )

    # # Profile detectron2 model
    # (
    #     elapsed_time_detectron2,
    #     start_cpu_detectron2,
    #     end_cpu_detectron2,
    #     start_memory_detectron2,
    #     end_memory_detectron2,
    # ) = profile_cpu_memory("detectron2_onnx", "zoutput-detectron2.txt")
    # print(f"Time taken for detectron2: {elapsed_time_detectron2} seconds")
    # print(f"CPU usage for detectron2: {end_cpu_detectron2 - start_cpu_detectron2}%")
    # print(
    #     f"Memory usage for detectron2: {end_memory_detectron2 - start_memory_detectron2} bytes"
    # )
