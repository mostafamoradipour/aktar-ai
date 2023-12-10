from aktarai import Orchestrator
import yaml


if __name__ == "__main__":
    with open("config.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    user = cfg["user"]
    cfg = cfg[user]["ai"]
    orchestrator = Orchestrator(cfg)
    orchestrator.run()
