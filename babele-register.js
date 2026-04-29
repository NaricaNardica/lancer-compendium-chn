Hooks.once('init', () => {

	if(typeof Babele !== 'undefined') {

		Babele.get().register({
			module: 'lancer-compendium-chn',
			lang: 'cn',
			dir: 'zh_Hans'
		});

		Babele.get().registerConverters({
			"nameShunt": nameShunt,
			"generalConverter": generalConverter
		});
	}
});

function nameShunt(value, _trans, data, compendium) {
    if (!data) return value;
    const rawName = data.name;
    const translations = compendium.translations;

    // 1. 核心逻辑：先找一模一样的（区分大小写）
    // 这能让 "Lay Mines" 直接命中 K 版词条
    let entry = translations[rawName];

    // 2. 备选逻辑：如果没找到，且当前名字不是全大写，才去试全大写
    // 这样避免了 K 版去误撞原版的词条
    if (!entry && rawName && rawName !== rawName.toUpperCase()) {
        entry = translations[rawName.toUpperCase()];
    }

    // 3. ID 保底
    if (!entry) {
        entry = translations[data._id];
    }

    if (!entry) return value;
    return entry.name || value;
}

function generalConverter(system, _trans, data, compendium) {
    if (!data || !system) return system;
    const rawName = data.name;
    const translations = compendium.translations;

    // 逻辑必须与 nameShunt 保持高度一致
    let entry = translations[rawName];

    if (!entry && rawName && rawName !== rawName.toUpperCase()) {
        entry = translations[rawName.toUpperCase()];
    }

    if (!entry) {
        entry = translations[data._id];
    }

    if (!entry) return system;

    let retObj = Object.assign({}, system);
    const lid = system.lid;

    // 处理变体 LID（如播种机[K]特有的内容）
    if (lid && entry[lid]) {
        return objectConvert(retObj, entry[lid]);
    }
    
    return objectConvert(retObj, entry);
}


function objectConvert(source, translate) {
	if (translate == undefined) return source;
	
	for (const key of Object.keys(translate)) {
		if (source[key] == undefined) {
			continue;
		}

		if (Array.isArray(source[key])) {
			for (const entry of source[key]) {
				objectConvert(entry, translate[key][entry.name]);
			}
		} else if (typeof source[key] === "object") {
			objectConvert(source[key], translate[key]);
		} else {
			source[key] = translate[key];
		}
	}
	return source;
}