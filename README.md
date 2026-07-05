# Papers

読んだ論文の AI 要約を Markdown で管理する Hugo site です。

## Add a Paper with Gemini

Gemini に論文 URL を渡して、このリポジトリ用の Markdown を生成させるときは、[prompts/add-paper-with-gemini.txt](prompts/add-paper-with-gemini.txt) のプロンプトを使います。

生成後、HTML コメントの slug を使って `content/papers/{slug}.md` として保存します。

## Local Preview

```sh
hugo server -D
```

ローカルでは `http://localhost:1313/` または `http://localhost:1313/papers/` を開きます。
