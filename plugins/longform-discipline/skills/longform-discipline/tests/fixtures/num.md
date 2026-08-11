# 設計書

## 第1章 要件

応答時間は200msを上限とする。同時接続数は1000人を想定する。
保持期間は90日とする。

| 項目 | 値 |
|---|---|
| 応答時間 | 300ms |

## 第2章 設計

キューの深さは64個とする。応答時間は200msで設計する。

## 第3章 評価

計測の結果、応答時間は500msであった。同時接続数は1000人まで確認した。
保持期間は30日に短縮した。

> 引用: 応答時間は50msである。

## 第4章 まとめ

The latency budget is 200 ms. The retention period is 90 days.

## 第5章 付録

The latency budget is 400 ms. Throughput reached 1000 tokens.
