import './App.css';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import React, { useEffect } from 'react'

const defaultQuickReplies = [
  {
    icon: 'message',
    name: 'c c++ c#',
  },
  {
    icon: 'message',
    name: 'python',
  },
  {
    icon: 'message',
    name: 'Java',
  },
  {
    icon: 'message',
    name: 'javascript',
  },
  {
    icon: 'message',
    name: 'golang',
  },
  {
    name: 'GPT',
    isNew: true,
    isHighlight: true,
  },
];


const initialMessages = [
  {
    type: 'text',
    content: { text: '您好，我是AI编程助理，开源于：https://github.com/git-cloner/codegen，还提供VS Code插件codegeeker，注意python以冒号结尾，其他编程语言以{结尾。' },
    user: { avatar: '//gitclone.com/download1/gitclone.png' },
  },
  {
    type: 'image',
    content: {
      picUrl: '//gitclone.com/download1/aiit/extension.png',
    },
  },
];

function App() {
  const { messages, appendMsg, setTyping } = useMessages(initialMessages);

  function handleSend(type, val) {
    if (type === 'text' && val.trim()) {
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'right',
        user: { avatar: '//gitclone.com/download1/user.png' },
      });

      setTyping(true);

      onGenCode(val);
    }
  }

  function renderMessageContent(msg) {
    const { type, content } = msg;

    switch (type) {
      case 'text':
        return <Bubble content={content.text} />;
      case 'image':
        return (
          <Bubble type="image">
            <img src={content.picUrl} alt="" />
          </Bubble>
        );
      default:
        return null;
    }
  }

  function handleQuickReplyClick(item) {
    var content = "int add(int x,int y){";
    if (item.name === "c c++ c#") {
      content = "int add(int x,int y){";
    } else if (item.name === "python") {
      content = "def hello_world():";
    } else if (item.name === "Java") {
      content = "int add(int x,int y){";
    } else if (item.name === "javascript") {
      content = "function Add(x,y,z){";
    } else if (item.name === "golang") {
      content = "func IsBlacklist(bl []string,url string) bool{";
    } else {
      content = "写一个python版的数组排序";
    }
    handleSend('text', content);
  }

  function onGenCode(context) {
    var sl = context.trim().split("\n");
    context = sl[sl.length - 1];
    if (context.trim() === "") {
      alert("输入不能为空！")
      return;
    }
    let xhr = new XMLHttpRequest();
    xhr.open('post', 'https://gitclone.com/aiit/codegen');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
      var json = JSON.parse(xhr.response);
      context = context + "\n" + json.result;
      appendMsg({
        type: 'text',
        content: { text: context },
        user: { avatar: '//gitclone.com/download1/gitclone.png' },
      });
    }
    xhr.send('{"context":"' + context + '","maxlength":32}');
  }

  function findInArr(arr, n) {
    for (var i = 0; i < arr.length; i++) {
      if (arr[i] === n) return true;
    }
    return false;
  };

  function getByClass(oParent, sClass) {
    if (document.getElementsByClassName) {
      return oParent.getElementsByClassName(sClass);
    } else {
      var aEle = oParent.getElementsByTagName('*');
      var arr = [];
      for (var i = 0; i < aEle.length; i++) {
        var tmp = aEle[i].className.split(' ');
        if (findInArr(tmp, sClass)) {
          arr.push(aEle[i]);
        }
      }
      return arr;
    }
  }

  useEffect(() => {
    var oUl = document.getElementById('root');
    var aBox = getByClass(oUl, 'Input Input--outline Composer-input');
    if (aBox.length > 0) {
      aBox[0].focus();
    }
  })
  return (
    <div style={{ height: 'calc(100vh - 10px)', marginTop: '-5px' }}>
      <Chat
        navbar={{
          leftContent: {
            icon: 'chevron-left',
            title: 'Back',
          },
          rightContent: [
            {
              icon: 'apps',
              title: 'Applications',
            },
            {
              icon: 'ellipsis-h',
              title: 'More',
            },
          ],
          title: '基于Salesforce codegen和GPTJ、GPT-neo的AI代码生成',
        }}
        messages={messages}
        renderMessageContent={renderMessageContent}
        quickReplies={defaultQuickReplies}
        onQuickReplyClick={handleQuickReplyClick}
        onSend={handleSend}
      />
    </div>
  );
}

export default App;
