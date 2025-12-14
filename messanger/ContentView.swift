
import SwiftUI

struct MessageBubble: View {
    let message: Message
    var body: some View {
        HStack {
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                
                Text(message.text)
                    .font(.body)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(message.timeString)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding(.vertical, 6)
            .padding(.horizontal, 10)
            .background(Color.gray.opacity(0.2))
            .cornerRadius(12)
            .frame(maxWidth: 250, alignment: .trailing)
        }
        .padding(.horizontal)
    }
}

struct Message: Identifiable{
    let id = UUID()
    let text: String
    let time: Date
    var timeString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: time)
    }
}

struct ContentView: View {
    @State var input: String = ""
    @State var messages: [Message] = []
    @FocusState private var isInputFocused: Bool
    @State var showScrollButton: Bool = false
    @State var ScrollHeight: CGFloat = 0
    var body: some View {
        ScrollViewReader{ item in
            VStack(spacing: 4){
                ZStack{
                    ScrollView{
                        ForEach(messages){message in
                            MessageBubble(message: message).id(message.id)
                        }
                        GeometryReader { geo in
                            Color.clear
                                .allowsHitTesting(false).onChange(
                                    of: geo.frame(in: .named("Scrolling")).maxY
                                ) { _, maxY in
                                    showScrollButton = maxY > ScrollHeight+10
                                }
                        }.onTapGesture {
                            isInputFocused = false
                        }.onChange(of:messages.count) { _,_ in
                            if !showScrollButton{
                                if let lastId = messages.last?.id {
                                    withAnimation {
                                        item.scrollTo(lastId, anchor: .bottom)
                                    }
                                }
                            }
                            
                        }.frame(height: 1)
                        
                    }.simultaneousGesture(
                        TapGesture().onEnded {
                            isInputFocused = false
                        }
                    ).coordinateSpace(name: "Scrolling").background(
                        GeometryReader{ pos in
                            Color.clear.onAppear{
                                ScrollHeight = pos.size.height
                            }
                        }
                    )
                    VStack{
                        Spacer()
                        HStack{
                            Spacer()
                            Button{
                                showScrollButton = false
                                if let lastId = messages.last?.id {
                                    withAnimation {
                                        item.scrollTo(lastId, anchor: .bottom)
                                    }
                                }
                                
                                
                            }label: {
                                Image(systemName: "arrow.down.circle.fill").font(.largeTitle)
                            }.padding(.trailing,6).opacity(showScrollButton ? 1 : 0)
                        }
                    }
                }
                
                
                
                
                Spacer()
                
                
                HStack(alignment: .bottom){
                    TextField("сообщение",text: $input,axis: .vertical).padding().frame(maxWidth:310).background(.secondary).cornerRadius(16).foregroundColor(.primary).focused($isInputFocused)
                    Spacer()
                    VStack{
                        
                        Button{
                            if input != ""{
                                let new_mes = Message(text: input, time: Date())
                                messages.append(new_mes)
                                input = ""
                            }
                        } label: {
                            HStack{
                                Image(systemName: "paperplane.fill").font(.system(size: 26)).padding(10)
                            }
                            
                        }
                        .frame(width: 50,height: 50) .background(Circle().fill(.secondary)).padding(1).cornerRadius(22).foregroundColor(.primary)
                    }
                }.background(Color.clear)
                
                
            }
            .padding()
        }
    }
}
        

#Preview {
    ContentView()
}
