/* Match the actual work name first; fall back to the official work type. */
function hindiWorkType(v,name,mapping,code,sanction){
 if([24577,24961,25899,30899].includes(Number(String(sanction??'').replace(/[,₹\s]/g,''))))return 'ओपन डग वेल';
 const correctedWorks={"1712005003/AV/22012034653299":"खाद्यान्न भंडारण","1712004008/WC/22012035228726":"परकोलेशन टैंक","1712005080/IF/22012034993930":"खेत तालाब","1712008042/LD/22012034951218":"खेल मैदान","1712008001/LD/22012034939964":"नाली निर्माण","1712005058/LD/22012034590003":"खेल मैदान"};
 if(correctedWorks[String(code||'').trim()])return correctedWorks[String(code||'').trim()];

 const normalize=x=>String(x||'').normalize('NFKC').toLowerCase().replace(/\s+/g,' ').trim();
 const names=[
 [/\b(?:dug|duck|dag)[\s_-]*p(?:ond|ound|aund|and)s?\b|डग\s*पॉ[नण]्ड|डग\s*पोंड/,'डग पॉन्ड'],
 [/kapil[\s_-]*dhara.*recharge[\s_-]*(?:pit|fit)|कपिल\s*धारा.*(?:रिचार्ज|पुनर्भरण).*पि[टट्]/,'ओपन डग वेल'],
 [/^open dug well$|^पुनर्भरण पिट$|^रिचार्ज पिट$/,'ओपन डग वेल'],
 [/\b(?:pmay[\s_-]*g?|iay)\b|प्रधानमंत्री.*आवास|इंदिरा.*आवास/,'PMAY-G'],
 [/अमृ[तथ]\s*सरोवर|amr[iu]t[\s_-]*saro(?:var|war|ver)/,'अमृत सरोवर'],
 [/gabion|g[aeo]+b[iy]+[ao]?n|ग[ेैो]ब[िी]य?न|गेबियन|गोबियन|गैबियन/,'गेबियन'],
 [/soak[\s_-]*pit|sok[\s_-]*pit|shok[\s_-]*pit|सो[खक]\s*पि[टट्]/,'सोख पिट'],
 [/khet[\s_-]*ta[l]+ab|farm[\s_-]*pond|खेत\s*तालाब/,'खेत तालाब'],
 [/m[eai]+[dḍ]h?[\s_-]*b[a]+n?dh?(?:an)?|मे[ड़ढडध]़?\s*(?:बंध|बन्ध)|farm\s*bunding/,'मेढ़ बंधान'],
 [/charagah|charagaah|चारागाह|silvi.?pasture|grass.?land/,'चारागाह विकास'],
 [/food.?grain|agri.*produce.*storage|khad[a-z]*[\s_-]*bh[a]+n+d+h?[a]+r|(?:anaj|anaaj).*(?:godam|bh[a]+n+d+h?[a]+r)|(?:godam|bh[a]+n+d+h?[a]+r).*(?:anaj|anaaj)|खाद्या[नं्]*.*भ[ंँण]डार|अनाज.*(?:गोदाम|भंडार)|(?:गोदाम|भंडार).*अनाज|कृषि.*उपज.*भंडार/,'खाद्यान्न भंडारण'],
 [/bore[\s_-]*well[\s_-]*recharge|बोरवेल.*पुनर्भरण/,'ओपन डग वेल'],
 [/(?:open|dug|dag)[\s_-]*well[\s_-]*(?:recharge|rechrage)|कूप.*पुनर्भरण|कुए.*पुनर्भरण/,'ओपन डग वेल'],
 [/recharge\s*pit|रिचार्ज\s*पिट|पुनर्भरण\s*(?:गड्ढा|पिट)/,'ओपन डग वेल'],
 [/pul[iy]+a|culvert|पुलिया/,'पुलिया'],
 [/nali|grey.?water|drain|नाली/,'नाली निर्माण'],
 [/boundary[\s_-]*wall|compound[\s_-]*wall|cmp.?ond.*wall|बाउंड्री|चहारदीवारी/,'बाउंड्री वाल'],
 [/(?:तालाब|talab|pond).*(?:जीर्ण|जिर्ण|गहरीकरण|सुधार|jirn|gehr|gahr|sudhar)|renov.*pond|desilting/,'तालाब जीर्णोद्धार'],
 [/मत्स्य.*तालाब|fisher.*pond/,'डग पॉन्ड'],
 [/dug[\s_-]*pond|नवीन\s*तालाब|तालाब\s*निर्माण|talab\s*(?:nirman|nirmaan)/,'तालाब निर्माण'],
 [/kapil[\s_-]*dhara|कपिल\s*धारा/,'कपिल धारा कूप'],
 [/dug[\s_-]*well|open[\s_-]*well|koop|कूप|कुआँ|कुआ|कुए/,'कूप निर्माण'],
 [/stop[\s_-]*dam|स्टॉप\s*डैम|स्टाप\s*डेम/,'स्टॉप डैम'],
 [/check[\s_-]*dam|चेक\s*डैम|चेक\s*डेम/,'चेक डैम'],
 [/anicut|एनीकट|एनिकट/,'एनीकट'],
 [/percolation|parkul[ae]tion|parkuleshan|parcolation|परकोलेशन/,'परकोलेशन टैंक'],
 [/gully.*plug|गली.*प्लग/,'गली प्लग'],
 [/trench|ट्रेंच/,'कंटूर ट्रेंच'],
 [/play[\s_-]*(?:ground|field)|khel[\s_-]*ma[iy]?d[a]+n|खेल\s*मैदान/,'खेल मैदान'],
 [/bagiya|बगिया/,'एक बगिया'],
 [/plantation|vriksh|वृक्षारोपण|वृक्षारोपड|पौधरोपण|वृक्षारोपण/,'वृक्षारोपण'],
 [/(?:cc|pcc|सीसी|सी\.सी|सी सी).*?(?:road|sadak|मार्ग|रोड|सड़क)|cement.*concrete.*road/,'सीमेंट कंक्रीट सड़क'],
 [/interlocking|इंटरलॉक/,'इंटरलॉकिंग सड़क'],
 [/gr[ae]v[ae]?[l]|grewal|greval|ग्रेवल|ग्रेवाल/,'ग्रेवल रोड'],
 [/mur[au]m|मुरुम|मुरम|mitti.*(?:road|sadak)|मिट्टी.*सड़क/,'ग्रेवल रोड'],
 [/sudur|सुदूर|सुदुर/,'सुदूर सड़क'],
 [/(?:shanti|santi|shanthi|santhi)[\s_-]*dha(?:m|am)|शा(?:[ंँ]|न्)?त[िी]\s*धाम|crematorium/,'शांतिधाम'],
 [/gaushala|goushala|goshala|gowshala|गौ\s*शाला/,'गौशाला'],
 [/bharat[\s_-]*nirman[\s_-]*seva|भारत\s*निर्माण\s*सेवा|panchayat[\s_-]*(?:bhawan|bhavan)|पंचायत\s*भवन/,'पंचायत भवन'],
 [/angan[\s_-]*wadi.*toilet|आंगनवाड़ी.*शौचालय/,'आंगनवाड़ी शौचालय'],
 [/angan[\s_-]*wadi|आंगनवाड़ी|आँगनवाड़ी|^awc$/,'आंगनवाड़ी'],
 [/school.*toilet|विद्यालय.*शौचालय|स्कूल.*शौचालय/,'विद्यालय शौचालय'],
 [/sanitary.*complex|स्वच्छता.*परिसर/,'सामुदायिक स्वच्छता परिसर'],
 [/goat.*(?:shed|shelter)|बकरी.*शेड/,'बकरी शेड'],
 [/poultry|मुर्गी.*शेड/,'मुर्गी शेड'],
 [/piggery|सूकर.*शेड/,'सूकर शेड'],
 [/cattle.*(?:shed|shelter)|पशु\s*शेड/,'पशु शेड'],
 [/vermi|वर्मी/,'वर्मी कम्पोस्ट'],
 [/nadep|नाडेप/,'नाडेप'],
 [/compost|कम्पोस्ट/,'कम्पोस्ट पिट'],
 [/land.*(?:develop|level|shap)|भूमि.*(?:विकास|समतलीकरण)|समतलीकरण/,'भूमि समतलीकरण'],
 [/community.*hall|samudayik.*bhawan|सामुदायिक\s*भवन/,'सामुदायिक भवन']
 ];
 let t=normalize(name);
 // The first actual work term wins; later landmarks do not replace its type.
 let first=null;
 for(const [p,label] of names){const hit=p.exec(t);if(hit&&(!first||hit.index<first.index))first={index:hit.index,label};}
 if(first)return first.label;
 t=normalize(v);
 if(/cattle.*(?:shed|shelter).*community|सामुदायिक\s*पशु\s*शेड/.test(t))return 'गौशाला';
 for(const [p,label] of names)if(p.test(t))return label;
 const fallback=[
 [/constr.*gp.*community/,'पंचायत भवन'],
 [/levelling|leveling|shaping/,'भूमि समतलीकरण'],
 [/development.*land/,'भूमि विकास'],
 [/toilets.*school/,'विद्यालय शौचालय'],
 [/community.*pond/,'तालाब जीर्णोद्धार'],
 [/sand.*filter.*open.?well|open dug well/,'ओपन डग वेल'],
 [/sand.*filter.*bore.?well/,'ओपन डग वेल'],
 [/afforestation|pl[an]*tation|plntation|horticulture|for[e]?stry|shelter belt/,'वृक्षारोपण'],
 [/forest protection/,'वन संरक्षण'],
 [/raising.*nursery/,'पौधशाला'],
 [/cement.*concrete|^cement concrete$/,'सीमेंट कंक्रीट सड़क'],
 [/cement lining/,'सीमेंट अस्तरीकरण'],
 [/bund/,'मेड़ निर्माण'],
 [/embankment/,'तटबंध'],
 [/earthen.*dam/,'मिट्टी बांध'],
 [/boulder check/,'बोल्डर चेक डैम'],
 [/spur/,'स्पर निर्माण'],
 [/flood|diversion.*channel|feeder.*(?:canal|channel)|water courses.*canal/,'नहर निर्माण'],
 [/underground.*dyke/,'भूमिगत डाइक'],
 [/roof.*rain.*har/,'वर्षा जल संचयन'],
 [/water.*harvesting.*pond|sunken pond|^farm pond$/,'जल संचयन तालाब'],
 [/stabilization.*pond/,'जल स्थिरीकरण तालाब'],
 [/fish.*drying/,'मत्स्य सुखाने का प्लेटफॉर्म'],
 [/food grain/,'खाद्यान्न भंडारण'],
 [/cyclone shelter/,'चक्रवात आश्रय'],
 [/kitchen shed/,'रसोई शेड'],
 [/shg.*building/,'स्वयं सहायता समूह भवन'],
 [/workshed/,'आजीविका कार्यशाला'],
 [/rural haat/,'ग्रामीण हाट'],
 [/bio.*gas/,'बायोगैस संयंत्र'],
 [/biomanure/,'जैविक खाद संरचना'],
 [/building material/,'निर्माण सामग्री उत्पादन'],
 [/bitumen/,'डामर सड़क'],
 [/kharanja/,'खड़ंजा सड़क'],
 [/wbm/,'डब्ल्यूबीएम सड़क'],
 [/earthern road|earthen road/,'मिट्टी सड़क'],
 [/bench.*terrace/,'बेंच टेरेस'],
 [/chaur|waterlogged|water logged/,'जलभराव भूमि सुधार'],
 [/land.*develop|waste land/,'भूमि विकास'],
 [/maintenance.*public assets/,'सार्वजनिक परिसंपत्ति मरम्मत'],
 [/houses.*state|state scheme.*house/,'PMAY-G'],
 [/^well$|dugwells/,'कूप निर्माण'],
 [/^renovation$/,'जीर्णोद्धार'],
 [/^new construction$/,'नवीन निर्माण']
 ];
 for(const [p,label] of fallback)if(p.test(t))return label;
 const old=mapping&&mapping[v];
 if(old&&!/[a-z]/i.test(old))return old;
 return 'अन्य निर्माण कार्य';
}
