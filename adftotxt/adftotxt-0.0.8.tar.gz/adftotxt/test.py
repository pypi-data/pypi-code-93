import adftotxt

adf = {
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": []
    },
    {
      "type": "orderedList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "codeBlock",
              "attrs": {},
              "content": [
                {
                  "type": "text",
                  "text": "#include\nimport\nDIM"
                }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Hi There"
                }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Awesome"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "paragraph",
      "content": []
    }
  ]
}
print(adftotxt.parse(adf))