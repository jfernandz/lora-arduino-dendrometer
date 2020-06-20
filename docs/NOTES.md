# CrateDB

In order to get the CrateDB container working properly you have to set the `vm.max_map_count` to `262144` for systemd. This can be done by running

`sudo sysctl -w vm.max_map_count=262144`

As you can see in [CrateDB documentation](https://crate.io/docs/crate/howtos/en/latest/admin/bootstrap-checks.html#linux)


# Questions

 - [ ] **About the Linear Potentiometer:** In the [Product Details](https://uk.rs-online.com/web/p/potentiometers/0317780/?relevancy-data=636F3D3126696E3D4931384E525353746F636B4E756D626572266C753D656E266D6D3D6D61746368616C6C26706D3D5E2828282872737C5253295B205D3F293F285C647B337D5B5C2D5C735D3F5C647B332C347D5B705061415D3F29297C283235285C647B387D7C5C647B317D5C2D5C647B377D2929292426706F3D3126736E3D592673723D2673743D52535F53544F434B5F4E554D4245522677633D4E4F4E45267573743D3331372D373830267374613D3033313737383026&searchHistory=%7B%22enabled%22%3Atrue%7D) says: _"For best results, use as a potential divider (not variable resistor) and buffer the resulting output with a high impedance amplifier"_ Should I use a [TL081](https://www.st.com/resource/en/datasheet/tl081.pdf) or a [OPA341-¿OPA2341?](https://www.ti.com/lit/ds/sbos202a/sbos202a.pdf?ts=1591097396324) In fact, People in IRC suggested me to _"use a single supply rail-to-rail CMOS op-amp instead."_ because _"THose also have a very high input impedance"_; for example The OPA2341. 
 - [ ] The whole thing about use a regular rotary potentiometer.
 - [ ] I'm not using ® or ™ all the time [because of this](https://kermitmurray.com/msblog/trademark-symbols-in-scientific-writing)
 - [ ] Despite [here](https://www.semtech.com/products/wireless-rf/lora-transceivers/sx1276) doesn't say anything about single channel nature, I think it really it is, for instance, [LG-01 gateway](http://www.dragino.com/products/lora/item/143-lg01n.html) it is, and it does mount that chip.
 - [ ] This [arduino-lorawan](https://github.com/mcci-catena/arduino-lorawan) library apparently provides a more friendly interface between LoRa physical layer and TTN stack (which uses LoRaWAN protocol), however I'm using [arduino-lmic](https://github.com/mcci-catena/arduino-lmic) which is in fact a dependency for arduino-lorawan.
  - [ ] Differences between ABP and OTAA devices [here](https://static1.squarespace.com/static/560cc2c2e4b01e842d9fac18/t/5a938d38ec212d9451fbecf8/1519619387035/OTAA_or_ABPv3.pdf) and [here](https://www.thethingsnetwork.org/forum/t/what-is-the-difference-between-otaa-and-abp-devices/2723/2?u=electronics1920)