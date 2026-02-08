const { json } = require("stream/consumers");
if({{$json.needFinalSummary}}) {
  return [{ text: "Need Final Summary" }];
} else {
  return [{ text: "No Need Final Summary" }];
}