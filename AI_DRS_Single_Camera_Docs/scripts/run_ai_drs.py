#!/usr/bin/env python3
"""
Master CLI Entry Point for AI DRS — Single-Camera LBW Review System & Autonomous Match Engine
"""

import argparse
import sys
import uvicorn
from pathlib import Path

from ai_drs.api.review_service import ReviewPipelineService
from ai_drs.detection.dataset_trainer import DatasetTrainerEngine, DatasetTrainingConfig
from ai_drs.evaluation.final_certification import Final100MilestoneCertifier


def main():
    parser = argparse.ArgumentParser(description="AI DRS — Single-Camera LBW Review System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command 1: serve (Start FastAPI REST & WebSocket server)
    serve_parser = subparsers.add_parser("serve", help="Start FastAPI REST & WebSocket broadcast server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host address")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number")

    # Command 2: review (Process single video delivery)
    review_parser = subparsers.add_parser("review", help="Process delivery video review")
    review_parser.add_argument("--video", required=True, help="Path to input video file")
    review_parser.add_argument("--stance", default="RHB", choices=["RHB", "LHB"], help="Batter stance")

    # Command 3: train (Fine-tune model on dataset)
    train_parser = subparsers.add_parser("train", help="Fine-tune ball detection model on dataset")
    train_parser.add_argument("--dataset", default="C:\\Users\\Hello-pc\\Downloads\\archive (1)", help="Dataset path")
    train_parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")

    # Command 4: certify (Run 100-Milestone Master Certification)
    certify_parser = subparsers.add_parser("certify", help="Run 100-Milestone Master System Certification")

    args = parser.parse_args()

    if args.command == "serve":
        print(f"🚀 Starting AI DRS Production API Server on http://{args.host}:{args.port}")
        uvicorn.run("ai_drs.api.main:app", host=args.host, port=args.port, reload=False)

    elif args.command == "review":
        service = ReviewPipelineService()
        result = service.process_video(args.video, batter_stance=args.stance)
        print(f"🏏 AI DRS DECISION REVIEW RESULT:")
        print(f"  Decision: {result.result}")
        print(f"  Confidence: {result.confidence * 100:.1f}%")
        print(f"  Reason: {result.recommendation_reason}")

    elif args.command == "train":
        trainer = DatasetTrainerEngine(DatasetTrainingConfig(dataset_path=args.dataset, num_epochs=args.epochs))
        summary = trainer.train_custom_model()
        print(f"🎯 Model Fine-Tuning Complete:")
        print(f"  Train Images: {summary.total_train_images}, Test Images: {summary.total_test_images}")
        print(f"  Best mAP@50: {summary.best_map50:.3f}")
        print(f"  Output Model: {summary.model_output_path}")

    elif args.command == "certify":
        cert = Final100MilestoneCertifier.generate_final_certification()
        print(f"📜 100-MILESTONE MASTER SYSTEM CERTIFICATION:")
        print(f"  Status: {cert.certification_label}")
        print(f"  Passed Milestones: {cert.verified_milestones} / {cert.total_milestones}")
        print(f"  Pass Rate: {cert.pass_rate_pct:.1f}%")


    else:
        parser.print_help()


if __name__ == "__main__":
    main()
