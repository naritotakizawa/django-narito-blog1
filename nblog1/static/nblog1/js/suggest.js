const remove = e => {
    // 選択済みのアイテムをクリックした際、つまり削除処理。
    const suggestItem = e.target;
    const targetName = suggestItem.dataset.target;
    const pk = suggestItem.dataset.pk;
    const displayElement = document.getElementById(`${targetName}-display`);
    displayElement.removeChild(suggestItem);
    const formValuesElement = document.getElementById(`${targetName}-values`);
    const inputValueElement = document.querySelector(`input[name="${targetName}"][value="${pk}"]`);
    formValuesElement.removeChild(inputValueElement);

};

const createSuggestItem = element => {
    // サジェスト表示欄内で選択したアイテムの表示用データを作成する。
    const displayElement = document.getElementById(`${element.dataset.target}-display`);
    const suggestItem = document.createElement('p');
    suggestItem.dataset.pk = element.dataset.pk;
    suggestItem.dataset.target = element.dataset.target;
    suggestItem.textContent = element.textContent;
    suggestItem.classList.add('suggest-item');
    suggestItem.addEventListener('click', remove);
    displayElement.appendChild(suggestItem);
};

const createFormValue = element => {
    // サジェスト表示欄内で選択したアイテムの送信用データを作成する。
    const targetName = element.dataset.target;
    const formValuesElement = document.getElementById(`${targetName}-values`);
    const inputHiddenElement = document.createElement('input');
    inputHiddenElement.name = targetName;
    inputHiddenElement.type = 'hidden';
    inputHiddenElement.value = element.dataset.pk;
    formValuesElement.appendChild(inputHiddenElement);
};

const clickSuggest = e => {
    // サジェスト表示欄内のアイテムをクリックした際の処理
    const element = e.target;
    const targetName = element.dataset.target;
    const pk = element.dataset.pk;

    // そのアイテムが選択済みじゃないかを確認する
    if (!document.querySelector(`input[name="${targetName}"][value="${pk}"]`)) {
        document.getElementById(`${element.dataset.target}-input`).value = '';
        createSuggestItem(element);
        createFormValue(element);
    }
};


document.addEventListener('DOMContentLoaded', e => {
    for (const element of document.getElementsByClassName('suggest')) {
        const targetName = element.dataset.target;
        const suggestListElement = document.getElementById(`${targetName}-list`);

        // 全てのサジェスト入力欄に対しイベントを設定
        element.addEventListener('keyup', () => {
            const keyword = element.value;
            const url = `${element.dataset.url}?keyword=${keyword}`;
            if (keyword) {
                // 入力があるたびに、サーバーにそれを送信し、サジェスト候補を受け取る
                fetch(url)
                    .then(response => {
                        return response.json();
                    })
                    .then(response => {
                        const frag = document.createDocumentFragment();
                        suggestListElement.innerHTML = '';

                        // サジェスト候補を一つずつ取り出し、それを<li>要素として作成
                        // <li>要素をクリックした際のイベントも設定
                        for (const obj of response.object_list) {
                            const li = document.createElement('li');
                            li.textContent = obj.name;
                            li.dataset.pk = obj.pk;
                            li.dataset.target = targetName;
                            li.addEventListener('mousedown', clickSuggest);
                            frag.appendChild(li);
                        }

                        // サジェスト候補があればサジェスト表示欄に候補を追加し、display:block でサジェスト表示欄を見せる
                        if (frag.children.length !== 0) {
                            suggestListElement.appendChild(frag);
                            suggestListElement.style.display = 'block';

                        } else {
                            suggestListElement.style.display = 'none';
                        }

                    })
                    .catch(error => {
                        console.log(error);
                    });
            }
        });


        // 入力欄に対して、フォーカスが外れたらサジェスト表示欄を非表示にするよう設定
        element.addEventListener('blur', () => {
            suggestListElement.style.display = 'none';
        });
    }

    // 更新ページ等のように、ページ表示時に選択済みのデータがある場合
    // それをクリックすると消せるようにイベントを設定
    for (const element of document.getElementsByClassName('suggest-item')) {
        element.addEventListener('click', remove);
    }
});