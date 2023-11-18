from aktarai import Orchestrator
import yaml


if __name__ == "__main__":
    user = "mostafa"
    with open("config2.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]
    orchestrator = Orchestrator(cfg)
    orchestrator.run()
