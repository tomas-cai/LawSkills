# 平台化排版产物契约

## platform-layout.md

```markdown
# 平台排版方案：[文章标题]

## 1. 平台与阅读模型
- platform:
- audience:
- reading_model:
- assumptions:

## 2. 首屏方案
- title:
- subtitle_or_digest:
- cover:
- first_screen_promise:

## 3. 组件树
- block_id:
- block_type:
- reading_task:
- source_content:
- visual_treatment:
- image_slot:

## 4. 视觉令牌
- content_width:
- typography:
- colors:
- spacing:
- image_rules:

## 5. 平台改写记录
- preserved:
- split:
- condensed:
- moved:
- removed:

## 6. 质检与人工确认
- readability_score:
- visual_score:
- platform_fit_score:
- open_questions:
```

## layout-manifest.json

```json
{
  "version": "1.0",
  "platform": "wechat",
  "content_blocks": [],
  "image_slots": [],
  "visual_tokens": {
    "content_width": "",
    "typography": {},
    "colors": {},
    "spacing": {}
  },
  "metadata": {
    "title": "",
    "digest": "",
    "author": ""
  },
  "qa": {
    "readability": 0,
    "visual_beauty": 0,
    "platform_fit": 0,
    "status": "DRAFT"
  },
  "open_questions": []
}
```

状态只使用：`DRAFT`、`NEEDS_REVIEW`、`LAYOUT_READY`。没有完成视觉检查时不得使用 `LAYOUT_READY`。
