import './App.css';
import Chat, { Bubble, useMessages, Progress } from '@chatui/core';
import '@chatui/core/dist/index.css';
import '@chatui/core/es/styles/index.less';
import React, { useEffect, useState } from 'react';
import './chatui-theme.css';
import { marked } from "marked";
import packageJson from '../package.json'

var modelname = "ChatGLM-6b";
var lastPrompt = "";
var history = []

const defaultQuickReplies = [
  {
    icon: 'message',
    name: 'ChatGLM',
    isNew: true,
    isHighlight: true,
  },
  {
    icon: 'file',
    name: 'Vicuna',
    isNew: true,
    isHighlight: true,
  },
  {
    icon: 'chevron-up',
    name: '复制上个问题',
  }
];


const initialMessages = [
  {
    type: 'text',
    content: { text: '您好，请入编程、科学、技术、历史、文化、生活、趣味等领域的问题' },
    user: { avatar: '//gitclone.com/download1/gitclone.png' },
  }
];

function App() {
  const { messages, appendMsg, setTyping } = useMessages(initialMessages);
  const [percentage, setPercentage] = useState(0);
  const msgRef = React.useRef(null);

  function handleSend(type, val) {
    if (percentage > 0) {
      alert("正在生成中，请稍候，或刷新页面！");
      return;
    }
    if (type === 'text' && val.trim()) {
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'left',
        user: { avatar: '//gitclone.com/download1/user.png' },
      });
      setTyping(true);
      setPercentage(10);
      lastPrompt = val;
      onGenCode(val, 0);
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
    if (item.name.startsWith("复制")) {
      var oUl = document.getElementById('root');
      var aBox = getByClass(oUl, 'Input Input--outline Composer-input');
      if (aBox.length > 0) {
        aBox[0].value = lastPrompt;
        aBox[0].focus();
      }
      return;
    }
    if (item.name.startsWith("ChatGLM")) {
      modelname = "ChatGLM-6b";
    } else {
      modelname = "vicuna-7b";
    }
    handleSend('text', "你好");
  }

  function Sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  function markdown(code) {
    return marked(code);
  }

  async function onGenCode(prompt, count) {
    var stop = false;
    var x = 120;
    var result = "";
    await Sleep(500);
    if (count >= x) {
      setPercentage(0);
      return;
    }
    let xhr = new XMLHttpRequest();
    xhr.open('post', 'https://gitclone.com/aiit/codegen_stream/v2');
    //xhr.open('post', 'http://localhost:5000/codegen_stream/v2');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
      var json = JSON.parse(xhr.response);
      result = json.response;
      stop = json.stop;
      history = json.history;
      if (count === 0) {
        result = markdown(result);
        appendMsg({
          type: 'text',
          content: { text: "" },
          user: { avatar: '//gitclone.com/download1/gitclone.png' },
        });
        setTimeout(() => { updateMsg(result); }, 200);
      } else {
        updateMsg(result);
      }
      count++;
      setPercentage(count * 10);
      if (stop) {
        setPercentage(0);
        return;
      }
      onGenCode(prompt, count);
    }
    //只保留5个历史对话
    if (history.length>5){
      history.shift() ;
    }
    var context = JSON.stringify({
      "context": {
        "prompt": prompt,
        "history": history
      },
      "modelname": modelname
    });
    xhr.send(context);

    function updateMsg(context) {
      context = markdown(context);
      var oUl = document.getElementById('root');
      var aBox = getByClass(oUl, 'Bubble text');
      if (aBox.length > 0) {
        aBox[aBox.length - 1].innerHTML = "<p>" + context + "</p>";
        var msgList = getByClass(oUl, "PullToRefresh")[0];
        msgList.scrollTo(0, msgList.scrollHeight);
      }
    }
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

  function onRightContentClick() {
    window.history.go(0);
  }

  function onInputFocus(e){
    if (msgRef && msgRef.current) {
      msgRef.current.scrollToEnd() ;
    }
  }

  function onLeftContentClick() {
    const name = packageJson.name;
    const version = packageJson.version;
    window.alert(name + '\n' + version);
  }

  useEffect(() => {
    var oUl = document.getElementById('root');
    var aBox = getByClass(oUl, 'Input Input--outline Composer-input');
    if (aBox.length > 0) {
      aBox[0].focus();
    }
  })

  return (
    <div style={{ height: 'calc(100vh - 2px)', marginTop: '-5px' }}>
      <Chat
        navbar={{
          leftContent: {
            icon: 'apps',
            title: '关于',
            onClick: onLeftContentClick,

          },
          rightContent: [
            {
              icon: 'refresh',
              title: '刷新',
              onClick: onRightContentClick,
            },
          ],
          title: 'AIITChat(' + modelname + ')',
        }}
        messages={messages}
        messagesRef={msgRef}
        renderMessageContent={renderMessageContent}
        quickReplies={defaultQuickReplies}
        onQuickReplyClick={handleQuickReplyClick}
        onSend={handleSend}
        placeholder="请输入您的问题，shift + 回车换行"
        onInputFocus={onInputFocus}
      />
      <Progress value={percentage} />
    </div>
  );
}

export default App;
