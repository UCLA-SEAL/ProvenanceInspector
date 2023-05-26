import os
import glob
import logging
import torch
import pandas as pd
import hydra
from omegaconf import DictConfig, OmegaConf

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

from utils import *
from extractors import (
    PerformanceExtractor,
    AlignmentMetric,
    GrammarMetric,
    FluencyMetric
)

torch.use_deterministic_algorithms(False)

@hydra.main(version_base=None, config_path="./conf", config_name="config")
def quality(cfg: DictConfig):

    #############################################################
    ## Initializations ##########################################
    #############################################################

    log = logging.getLogger(__name__)

    log.info("Starting quality evaluation...")
    log.info(OmegaConf.to_yaml(cfg))

    log.info("Setting up working directories.")
    os.makedirs(cfg.results_dir, exist_ok=True)

    device = torch.device('cpu')
    if torch.cuda.is_available():
        os.environ["CUDA_VISIBLE_DEVICES"] = str(cfg.robustness.visible_cuda_devices)
        device = torch.device('cuda')
    log.info(f"training on device={device}")    

    #############################################################
    ## Load dataset #############################################
    #############################################################

    if "csv" not in cfg.quality.dataset_path:
        raise ValueError("dataset_path expected to be csv...")
    evaluation_dataset = load_dataset("csv", data_files=cfg.quality.dataset_path)["train"]

    print(evaluation_dataset.num_rows)
    
    log.info(f"evaluation_dataset: {evaluation_dataset}")

    # load comparison dataset of same size as the provided dataset
    raw_datasets = load_dataset(cfg.dataset.builder_name, 
                                cfg.dataset.config_name)
    
    if 'sst2' in cfg.dataset.config_name:
        raw_datasets.pop("test") # test set is not usable (all labels -1)

    log.info("Preparing datasets splits...")
    raw_datasets = prepare_splits(raw_datasets)
    raw_datasets = rename_text_columns(raw_datasets)
    raw_datasets = remove_unused_columns(raw_datasets)
    raw_datasets = raw_datasets.shuffle()

    comparison_dataset = raw_datasets["validation"].select(range(len(evaluation_dataset)))
    
    log.info(f"comparison_dataset: {comparison_dataset}")

    #############################################################
    ## Model + Tokenizer ########################################
    #############################################################

    log.info("Loading quality model...")
    tokenizer = AutoTokenizer.from_pretrained(cfg.quality.model_id)
    model = AutoModelForSequenceClassification.from_pretrained(cfg.quality.model_id).to(device)

    #############################################################
    ## Initializing Extractors ##################################
    #############################################################
    
    log.info("Initializing metric extractors...")
    perf_extractor = PerformanceExtractor(model=model, tokenizer=tokenizer)
    a_metric = AlignmentMetric(
        builder_name=cfg.dataset.builder_name, 
        config_name=cfg.dataset.config_name,
        model_id=cfg.alignment_extractor.model_id)
    f_metric = FluencyMetric()
    g_metric = GrammarMetric()

    #############################################################
    ## Quality Evaluations ######################################
    #############################################################

    out = {}
    out.update({
        "quality_model_id":      cfg.quality.model_id,
        "dataset.builder_name":  cfg.dataset.builder_name,
        "dataset.config_name":   cfg.dataset.config_name,
        "dataset_size":          len(evaluation_dataset),
    })

    log.info("Extracting alignment scores...")
    evaluation_dataset, a_scores_eval = a_metric.evaluate(evaluation_dataset)
    comparison_dataset, a_scores_comp = a_metric.evaluate(comparison_dataset)
    a_scores_eval = a_scores_eval.mean()
    a_scores_comp = a_scores_comp.mean()
    out["eval_alignment"] = a_scores_eval
    out["comp_alignment"] = a_scores_comp
    out["alignment_score"] = out["eval_alignment"] / out["comp_alignment"] 

    log.info("Extracting fluency scores...")
    evaluation_dataset, f_scores_eval = f_metric.evaluate(evaluation_dataset)
    comparison_dataset, f_scores_comp = f_metric.evaluate(comparison_dataset)
    f_scores_eval = f_scores_eval.mean()
    f_scores_comp = f_scores_comp.mean()
    out["eval_fluency"] = f_scores_eval
    out["comp_fluency"] = f_scores_comp
    out["fluency_score"] = out["comp_fluency"] / out["eval_fluency"]

    log.info("Extracting grammaticality scores...")
    evaluation_dataset, g_scores_eval = g_metric.evaluate(evaluation_dataset)
    evaluation_dataset, g_scores_comp = g_metric.evaluate(comparison_dataset)
    g_scores_eval = g_scores_eval.mean()
    g_scores_comp = g_scores_comp.mean()
    out["eval_grammaticality"] = g_scores_eval
    out["comp_grammaticality"] = g_scores_comp
    out["grammaticality_score"] = out["comp_grammaticality"] / out["eval_grammaticality"]

    log.info("Extracting model perfromance scores...")
    p_scores_eval = perf_extractor.extract_performance(evaluation_dataset)
    p_scores_comp = perf_extractor.extract_performance(comparison_dataset)
    out["eval_gutcheck_accuracy"]   = p_scores_eval["accuracy"]
    out["eval_gutcheck_precision"]  = p_scores_eval["precision"]
    out["eval_gutcheck_recall"]     = p_scores_eval["recall"]
    out["eval_gutcheck_f1"]         = p_scores_eval["f1"]
    out["comp_gutcheck_accuracy"]   = p_scores_comp["accuracy"]
    out["comp_gutcheck_precision"]  = p_scores_comp["precision"]
    out["comp_gutcheck_recall"]     = p_scores_comp["recall"]
    out["comp_gutcheck_f1"]         = p_scores_comp["f1"]
    out["gutcheck_accuracy_score"]  = out["eval_gutcheck_accuracy"]  / out["comp_gutcheck_accuracy"] 
    out["gutcheck_precision_score"] = out["eval_gutcheck_precision"] / out["comp_gutcheck_precision"] 
    out["gutcheck_recall_score"]    = out["eval_gutcheck_recall"]    / out["comp_gutcheck_recall"] 
    out["gutcheck_f1_score"]        = out["eval_gutcheck_f1"]        / out["comp_gutcheck_f1"] 

    print(out)

    return out

if __name__ == "__main__":
    quality()