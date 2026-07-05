---
title: "RovoDev Code Reviewer: A Large-Scale Online Evaluation of LLM-based Code Review Automation at Atlassian"
authors:
  - "Kla Tantithamthavorn"
  - "Yaotian Zou"
  - "Andy Wong"
  - "Michael Gupta"
  - "Zhe Wang"
  - "Mike Buller"
  - "Ryan Jiang"
  - "Matthew Watson"
  - "Minwoo Jeong"
  - "Kun Chen"
  - "Ming Wu"
year: 2026
venue: "ICSE-SEIP '26"
paper_url: "https://arxiv.org/abs/2601.01129"
tags: ["LLM", "Code Review", "Software Engineering", "Online Evaluation"]
summary: "Atlassian の RovoDev Code Reviewer を、1,900 超のリポジトリと 54,000 超の生成コメントで 1 年間評価した産業事例。生成コメントの 38.70% が後続コミットでのコード変更につながり、PR サイクル時間の短縮や人間のレビューコメント数削減も報告している。"
---

## 一言でいうと

LLM によるコードレビューコメント生成を、オフライン指標だけでなく Atlassian の実運用環境で大規模に評価した論文。RovoDev Code Reviewer は、fine-tuning なしのゼロショット生成、LLM-as-a-Judge による事実性チェック、ModernBERT による actionability チェックを組み合わせ、実際の Pull Request にコメントを投稿する。

## 背景

コードレビューは品質保証の中核だが、大規模開発ではレビュー待ちがボトルネックになる。既存研究では LLM を使ったレビューコメント生成が進んでいるものの、企業環境では次の問題が残る。

- 顧客コードやメタデータを fine-tuning に使いにくい
- 社内レビューガイドラインを反映したコメント生成が必要
- 新規プロジェクトでは履歴データを使った RAG が効きにくい
- LLM のコメントは曖昧、非 actionable、事実誤認になり得る
- BLEU や semantic similarity のようなオフライン指標だけでは、実際に開発者の行動を変えたか分からない

この論文は、レビューコメントが実際にコード変更や PR サイクルへどう影響するかをオンライン評価で測る点が主眼。

## 手法

RovoDev Code Reviewer は、Bitbucket 上の Pull Request に統合されたコードレビュー自動化ツールとして設計されている。構成は大きく 3 つ。

1. ゼロショットの context-aware / review-guided コメント生成
   - PR タイトル、説明、関連ファイル、Jira issue 情報などを使う
   - persona、task definition、chain-of-thought、レビューガイドラインを含む structured prompt を使う
   - 顧客データで fine-tuning しない

2. 事実性チェック
   - LLM-as-a-Judge で、生成コメントが対象 PR や変更行と整合しているかを判定する
   - 不正確、無関係、矛盾、不自然なコメントを落とす

3. actionability チェック
   - ModernBERT ベースの分類器で、開発者が解決可能なコメントかを判定する
   - vague / non-actionable なコメントを除外する

評価は、1 年間にわたる Atlassian 内部での実運用データを使う。対象は 1,900 超のリポジトリ、生成コメントは 54,000 超。主な評価観点は、生成コメントが後続コミットでのコード変更につながった割合、PR サイクル時間、人間が書くレビューコメント数、開発者の定性的フィードバック。

## 結果

主な報告値は以下。

- RovoDev 生成コメントの code resolution rate は 38.70%
- 人間のレビューコメントの code resolution rate は 44.45%
- RovoDev 導入により median PR cycle time が 30.8% 減少
- 人間が書くレビューコメント数が 35.6% 減少
- 開発者は、正確なエラー検出や actionable な提案に価値を感じた
- 一方で、必要な文脈が不足している場合には不正確または non-actionable なコメントが出ることもある

重要なのは、LLM コメントが人間コメントより常に優れているという主張ではなく、実運用上の補助レビューとして一定割合でコード変更を促し、レビューサイクルを短縮する可能性を示した点。

## 限界

- Atlassian 内部の Bitbucket / Jira を前提にした評価なので、他組織や GitHub / GitLab で同じ効果が出るとは限らない
- code resolution rate は実用的な指標だが、すべてのコード変更が品質改善とは限らない
- 人間コメントとの比較では、コメントの目的や粒度が完全に一致していない可能性がある
- RovoDev がコメントしなかったケース、またはフィルタで落としたコメントの潜在的価値は見えにくい
- 産業導入論文なので、モデルプロンプトや内部データの詳細は再現しにくい

## 自分用メモ
