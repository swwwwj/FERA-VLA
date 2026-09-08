"""Summarize measured acceptance results; never mark missing experiments complete."""
import json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    def read(name):
        p=root/name
        return json.loads(p.read_text()) if p.exists() else None
    smoke=read("outputs/smoke/result.json")
    determinism=read("outputs/determinism/result.json")
    summary=dict(smoke_passed=bool(smoke and smoke["passed"]),
                 determinism_passed=determinism["passed"] if determinism else None,
                 collection_approved=False,scientific_hypotheses_tested=False)
    if determinism:
        checks=determinism["checks"]
        summary.update(state_max=max(c["state_max"] for c in checks),
                       state_mse_max=max(c["state_mse"] for c in checks),
                       rgb_max=max(c["rgb_max"] for c in checks),
                       success_agreement_min=min(c["success_agreement"] for c in checks),
                       repeat_checks=len(checks))
    (root/"reports/verification.json").write_text(json.dumps(summary,indent=2)+"\n")
    (root/"reports/status.md").write_text(
        "# 首版框架状态\n\n"
        "远端独立 Conda 环境、官方 LIBERO 固定版本、适配层、重放快照、候选采样、"
        "门控分叉执行接口、结果结构、保守标签、轨迹分组、动作距离及 MLP 工厂已实现。\n\n"
        "## 实测验收\n\n" + json.dumps(summary,indent=2) + "\n\n"
        "100步随机动作冒烟：libero_goal/0，双相机128×128，7维动作；已保存20帧并人工检查示例。"
        "随机动作未完成任务，不能视为专家成功轨迹。\n\n"
        "重放检查仅覆盖随机小动作；不是接触丰富专家状态的最终验收。"
        "collection_approved 始终为 false，尚未开始800分叉或模型训练。\n\n"
        "## 环境限制\n\n"
        "- NVIDIA CUDA设备可见，但 EGL 实测为 Mesa llvmpipe 软件渲染；系统缺少 NVIDIA EGL库/入口。\n"
        "- 环境使用CPU版 PyTorch，仅供初态加载及轻量评分器；未修改全局CUDA或其他项目环境。\n"
        "- GitHub远端直连可用，原有代理失效；本地推送使用本地代理。\n"
        "- Hugging Face直连连接超时，演示数据下载路径尚待解决。\n\n"
        "## 下一阶段\n\n"
        "实现两个任务的专家演示导入与成功重放、接触状态快照验收、任务特定安全/进度提取器；"
        "其后完成约800个分叉、人工标签审计和三种子基线/评分器评估。"
        "详细模块边界见 docs/architecture.md。\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
